#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import click
import json
import logging

from flask.ext.script import Manager
from miriam import create_app, app, logger, socketio

manager = Manager(app)

@manager.command
def runserver():
  "Runs the App"
  create_app()
  socketio.run(
    app,
    host=app.config['SERVE_HOST'],
    port=app.config['SERVE_PORT'],
    log_output=True
  )

@manager.command
@manager.option('-o', '--out', help='Path to store the computed graph')
def compute_graph(out):
  "Computes and Persists the Complex Data."
  from packrat.migration.graph import grow_network

  with open('data_dump/catalogue.json') as m:
    catalogue = json.load(m)

  target_file = catalogue['network']['targets']['path']
  host_file = catalogue['network']['hosts']['path']
  grow_network(target_file, host_file, out)

@manager.command
def compute_ranks(output, namespace, tissue):
  from packrat.computation.ranking import ranking_routine
  ranking_routine(output, tissue, namespace)

@manager.command
def datadownload():
  create_app()

  from miriam.graph.model import graph
  from packrat import spawn_gene_dat, spawn_ensembl_dat

  genes = [g for g, v in graph.node.items() if v['kind'] == 'GEN']

  for gene in genes:
    spawn_gene_dat(gene)
    spawn_ensembl_dat(gene)

  app.logger.info('Scheduled {0} Download Routines.'.format(len(genes) * 2))

@manager.command
def migrate_mirna():
  from Bio import SeqIO
  from miriam.graph.model import graph
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
  from miriam.graph.model import graph
  from packrat.migration.expression import dump_expression_dat

  with open('data_dump/catalogue.json') as m:
    data_path = json.load(m)

  exprs = data_path['expression']
  genes = [g for g, v in graph.node.items() if v['kind'] == 'GEN']

  for expr in exprs:
    dump_expression_dat(expr['path'], expr['namespace'], bunch=genes)

@manager.command
def migrate_ranks():
  "Migrates the Computed Ranks to the Metadata and Object DB"
  from packrat.migration.ranking import register_precomputed_ranking

  with open('data_dump/catalogue.json') as m:
    catalogue = json.load(m)

  register_precomputed_ranking(catalogue['computed_ranks'])

@manager.command
def setup_index():
  """
  Sets up the Search Index from MongoDB collections.
  """

  from miriam.search.indexer import Indexer
  from packrat import db

  def normalise_gene_doc(doc):
    """
    Normalise the docs.
    """
    kwd_fields = ['protein_ref', 'functions', 'processes', 'synonyms']
    join_list = lambda x: ', '.join(doc.get(x, []))
    return {
      'id': doc.get('gene_id'),
      'kind': 'Gene',
      'symbol': doc.get('symbol', doc['gene_id']),
      'kwd_doc': ' '.join([join_list(_) for _ in kwd_fields]),
      'sum_doc': doc.get('summary', ''),
    }

  normalise_mirna_doc = lambda doc: {
    'id': doc['mir_id'],
    'kind': 'MiRNA',
    'symbol': doc['mir_id'],
  }

  logger.info("Starting Indexing.")

  Indexer.index([
    [db['ncbi_gene_docs'].find(), normalise_gene_doc],
    [db['mirna_seq'].find(), normalise_mirna_doc]
  ])

  logger.info("Indexing Complete.")

if __name__ == "__main__":
  manager.run()
