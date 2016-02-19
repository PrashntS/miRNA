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

  from miRNA.graph.model import graph
  from packrat import spawn_gene_dat

  genes = [g for g, v in graph.node.items() if v['kind'] == 'GEN']

  for gene in genes:
    spawn_gene_dat(gene)

  app.logger.info('Scheduled {0} Download Routines.'.format(len(genes)))

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
