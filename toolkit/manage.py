#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import click
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

      print("Inserted Gene: {0} in MongoDB and Redis".format(str(g)))

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

      if len(meta.get('Host Gene', '')) > 0:
        gene_id = meta.get('Host Gene', '')
        weight = meta.get('Host Gene Transcript Count', 0.5)

        G.add_edge(gene_id, mir_id, weight = weight)

      print("Inserted miRNA: {0}".format(str(m)))

  #: Insert miRNA targets
  with open('data_dump/mirna_target_gene_affinity.json') as minion:
    targets = json.load(minion)

    for mir_id, trg in targets.items():
      #: Add the miRNA node

      count = 0
      for gene_id, weight in trg:
        G.add_edge(mir_id, gene_id, weight = weight)
        count += 1

      print("Updated miRNA: {0} with {1} targets".format(str(m), str(count)))

  root = zdb.open().root()
  root['nxGraph'] = G
  transaction.commit()

@manager.command
def setup_db():
  from pymongo import MongoClient
  from miRNA.config import MONGODB_DB, MONGODB_HOST, MONGODB_PORT

  client = MongoClient(MONGODB_HOST, MONGODB_PORT)
  client.drop_database(MONGODB_DB)

  migrate()

if __name__ == "__main__":
  manager.run()
