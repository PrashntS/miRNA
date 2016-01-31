#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import click
import json
import meinheld

from flask.ext.script import Manager
from miRNA import create_app, app

manager = Manager(app)

@manager.command
def runserver():
  "Runs the App"
  create_app()
  if app.config['MEINHELD']:
    meinheld.listen((app.config['SERVE_HOST'],
                     app.config['SERVE_PORT']))
    meinheld.run(app)
  else:
    app.run(host     = app.config['SERVE_HOST'],
            port     = app.config['SERVE_PORT'],
            threaded = app.config['THREADED'])

@manager.command
def precompute():
  "Computes and Persists the Complex Data."
  create_app()
  from miRNA.procedure.migration import graph

  with open('data_dump/catalogue.json') as m:
    data_path = json.load(m)

  graph_path = data_path['mir_gene_graph']['path']

  app.logger.info('Precomputing the network at {0}'.format(graph_path))
  with open(graph_path) as minion:
    host_map_dat = json.load(minion)
    graph(host_map_dat)

@manager.command
def datadownload():
  create_app()

  from pandas import DataFrame

  from miRNA import zdb
  from packrat import scrape
  from packrat.scrapers import ncbigene

  g = zdb.root.nxGraph

  with open('data_dump/catalogue.json') as m:
    data_path = json.load(m)
  gene_map = data_path['gene_mapping']['path']

  app.logger.info('Initializing the Gene Mapping Routine')
  df = DataFrame.from_csv(gene_map, sep="\t").to_dict()['Entrez Gene ID']
  gene_nodes = [k for k, v in g.node.items() if v.get('kind') == 'GEN']

  missed = set()
  ezids = set()

  c1, c2 = [0, 0]
  for eid in gene_nodes:
    try:
      url = 'http://www.ncbi.nlm.nih.gov/gene/{0}'.format(int(df[eid]))
      scrape(url, ncbigene, eid, 'ncbigene')
      c1 += 1
    except (ValueError, IndexError, KeyError):
      missed.add(eid)
      c2 += 1

  app.logger.info('Scheduled {0} Download Routines, Missed {1}.'.format(c1, c2))

@manager.command
def migrate():
  "Populates the MongoDB database using the data_dump JSON"
  create_app()

  import json
  import networkx as nx
  import transaction

  from mongoengine.queryset import DoesNotExist

  from miRNA import zdb
  from miRNA.polynucleotide.model import Gene, miRNA as miRNAModel

  G = nx.DiGraph()
  miRNANodes = set()
  geneNodes = set()
  InEdge = {}
  OutEdge = {}

  #: Insert the Gene Data.
  with open('data_dump/gene_metadata.json') as minion:
    genes = json.load(minion)

    for gene_id, meta in genes.items():
      g = Gene()
      g.symbol = gene_id
      g.names  = meta.get('names', [])
      g.description = meta.get('description', '')
      g.save()

      G.add_node(gene_id, kind='Gene')

      geneNodes.add(gene_id)

      print("Inserted Gene: {0}".format(str(g)))

  #: Insert the miRNA Data.
  with open('data_dump/miRNA_metadata.json') as minion:
    mirs = json.load(minion)

    for mir_id, meta in mirs.items():
      m = miRNAModel()
      m.symbol = mir_id
      m.FASTA  = meta.get('miRNA Sequence', '')
      m.mirbase_url = meta.get('mature miRNA entry', '')
      m.save()

      G.add_node(mir_id, kind='miRNA')

      miRNANodes.add(mir_id)

      if len(meta.get('Host Gene', '')) > 0:
        gene_id = meta.get('Host Gene', '')
        weight = meta.get('Host Gene Transcript Count', 0.5)

        G.add_edge(gene_id, mir_id, weight = weight)

        if not mir_id in InEdge.keys():
          InEdge[mir_id] = {}
        InEdge[mir_id][gene_id] = [weight,]

        if not gene_id in OutEdge.keys():
          OutEdge[gene_id] = {}

        OutEdge[gene_id][mir_id] = [weight, ]

      print("Inserted miRNA: {0}".format(str(m)))

  #: Insert miRNA targets
  with open('data_dump/mirna_target_gene_affinity.json') as minion:
    targets = json.load(minion)

    for mir_id, trg in targets.items():
      count = 0
      for gene_id, weight in trg:
        G.add_edge(mir_id, gene_id, weight = weight)
        count += 1

        if not gene_id in InEdge.keys():
          InEdge[gene_id] = {}
        InEdge[gene_id][mir_id] = [weight,]

        if not mir_id in OutEdge.keys():
          OutEdge[mir_id] = {}
        OutEdge[mir_id][gene_id] = [weight, ]

      print("Updated miRNA: {0} with {1} targets".format(str(mir_id), str(count)))

  root = zdb.root()
  root['nxGraph'] = G
  root['Nodes'] = {
    'miRNA': miRNANodes,
    'Gene': geneNodes,
  }

  root['Edges'] = {
    'In': InEdge,
    'Out': OutEdge,
  }

  transaction.commit()

@manager.command
def setup_index():
  create_app()

  from miRNA.polynucleotide.model import Gene, miRNA as miRNAModel
  from miRNA.search.indexer import Indexer

  print("Indexing Data")
  i = Indexer.index_setup([Gene, miRNAModel])
  print(i)

@manager.command
def setup_db():
  from pymongo import MongoClient
  from miRNA.config import MONGODB_DB, MONGODB_HOST, MONGODB_PORT

  client = MongoClient(MONGODB_HOST, MONGODB_PORT)
  client.drop_database(MONGODB_DB)

  migrate()

if __name__ == "__main__":
  manager.run()
