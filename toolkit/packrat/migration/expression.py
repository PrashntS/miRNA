#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import csv
import logging
from packrat import db

expre_meta = db['expre_meta']

def dump_expression_dat(filename, namespace, bunch=None):
  #: Register Fields in the Expression Metadata
  doc = {
    'origin': filename,
    'namespace': namespace,
    'db': 'expre_' + namespace
  }
  fields = []
  coll = db['expre_' + namespace]
  with open(filename) as m:
    rows = csv.DictReader(m, delimiter='\t')
    for row in rows:
      gene_name = row['Gene Name']
      if type(bunch) is list and gene_name in bunch:
        del row['Gene Name']
        del row['Gene ID']
        fields = list(row.keys())
        row['gene_id'] = gene_name
        coll.update({'gene_id': gene_name}, row, True)
        logging.info("Inserted: {0}".format(gene_name))

  doc['fields'] = fields
  expre_meta.update({'namespace': namespace}, doc, True)
