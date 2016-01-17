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

  from mongoengine.queryset import DoesNotExist

  from miRNA.polynucleotide.model import Gene, miRNA as miRNAModel, miRNAGeneTargetComplex, miRNAGeneTargetedByComplex

  #: Insert the Gene Data.
  with open('data_dump/gene_metadata.json') as minion:
    genes = json.load(minion)

    for gene_id, meta in genes.items():
      g = Gene()
      g.symbol = gene_id
      g.names  = meta.get('names', [])
      g.description = meta.get('description', '')
      g.searchable = meta.get('description', '') + ' '.join(meta.get('names', []))

      g.save()
      print("Inserted Gene: {0}".format(str(g)))

  #: Insert the miRNA Data.
  with open('data_dump/miRNA_metadata.json') as minion:
    mirs = json.load(minion)

    for mir_id, meta in mirs.items():
      m = miRNAModel()
      m.symbol = mir_id
      m.FASTA  = meta.get('miRNA Sequence', '')

      m.searchable = mir_id + meta.get('miRNA Sequence', '')

      try:
        g = Gene.objects.get(symbol = meta.get('Host Gene'))
        m.host = g
        m.searchable += g.searchable

        h_tc = meta.get('Host Gene Transcript Count', 0)
        if h_tc > 0:
          g.transcript_count = h_tc
          g.save()
      except DoesNotExist:
        "No Host Gene"
        pass

      count = 0

      m.mirbase_url = meta.get('mature miRNA entry', '')
      mtc = meta.get('miRNA Transcript Count', 0)
      try:
        mtc = int(mtc)
      except ValueError:
        mtc = 0
      m.transcript_count = mtc
      m.save()

      try:
        g = Gene.objects.get(symbol = meta.get('Host Gene'))
        g.host_of = m
        g.save()
      except DoesNotExist:
        "No Host Gene"
        pass

      #: We'll add targets later, first, we gotta just save transcript counts and host_of
      for gene in meta.get('Target Gene with Transcript Count', []):
        try:
          g = Gene.objects.get(symbol = gene[0])
          g.transcript_count = gene[1]
          g.save()
          count += 1
        except DoesNotExist:
          #: Move on
          pass

      print("Inserted miRNA: {0}, and updated {1} genes".format(str(m), str(count)))

  #: Insert miRNA targets
  with open('data_dump/mirna_target_gene_affinity.json') as minion:
    targets = json.load(minion)

    for mir_id, trg in targets.items():
      try:
        m = miRNAModel.objects.get(symbol = mir_id)
        count = 0
        for i in trg:
          try:
            g = Gene.objects.get(symbol = i[0])
            e = miRNAGeneTargetComplex()
            e.gene = g
            e.affinity = i[1]

            f = miRNAGeneTargetedByComplex()
            f.miRNA = m
            f.affinity = i[1]

            g.targeted_by.append(f)
            g.save()

            m.searchable += " {0}".format(i[0])
            m.targets.append(e)
            count += 1
          except DoesNotExist:
            pass
        m.save()
        print("Updated miRNA: {0} with {1} targets".format(str(m), str(count)))

      except DoesNotExist:
        pass

@manager.command
def setup_db():
  from pymongo import MongoClient
  from miRNA.config import MONGODB_DB, MONGODB_HOST, MONGODB_PORT
  client = MongoClient(MONGODB_HOST, MONGODB_PORT)
  client.drop_database(MONGODB_DB)
  migrate()

if __name__ == "__main__":
  manager.run()
