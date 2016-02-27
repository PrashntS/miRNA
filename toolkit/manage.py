#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import click
import json
import meinheld
import logging

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

  from miRNA.graph.model import graph
  from packrat import spawn_gene_dat, spawn_ensembl_dat

  genes = [g for g, v in graph.node.items() if v['kind'] == 'GEN']

  for gene in genes:
    spawn_gene_dat(gene)
    spawn_ensembl_dat(gene)

  app.logger.info('Scheduled {0} Download Routines.'.format(len(genes) * 2))

@manager.command
def migrate_mirna():
  from Bio import SeqIO
  from miRNA.graph.model import graph
  from packrat import db
  collection = db['mirna_seq']

  with open('data_dump/catalogue.json') as m:
    data_path = json.load(m)

  fasta_path = data_path['mir_seq']['path']

  mirnas = [m for m, v in graph.node.items() if v['kind'] == 'MIR']

  with open(fasta_path) as m:
    fastas =  SeqIO.to_dict(SeqIO.parse(m, 'fasta'))

    for mirna in mirnas:
      try:
        doc = {
          'mir_id': mirna,
          'fasta': [{
            'seq': str(fastas[mirna].seq),
            'id': str(fastas[mirna].id),
          }]
        }
        collection.update({'mir_id': mirna}, doc, True)
      except KeyError as e:
        print('Missed miRNA {0}'.format(mirna))

@manager.command
def migrate_expression():
  from miRNA.graph.model import graph
  from packrat.mango.expression import dump_expression_dat

  with open('data_dump/catalogue.json') as m:
    data_path = json.load(m)

  exprs = data_path['expression']
  genes = [g for g, v in graph.node.items() if v['kind'] == 'GEN']

  for expr in exprs:
    dump_expression_dat(expr['path'], expr['namespace'], bunch=genes)

@manager.command
def migrate():
  "Populates the MongoDB database using the data_dump JSON"
  create_app()

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
