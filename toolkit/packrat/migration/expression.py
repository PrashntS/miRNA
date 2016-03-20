#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
import re
import logging
import pandas as pd

from packrat import db
from miriam import psql
from packrat import catalogue

expre_meta = db['expre_meta']
clean = lambda varStr: re.sub('\W|^(?=\d)','_', varStr).lower()

def routine():
  #: Register Fields in the Expression Metadata
  for meta in catalogue['expression']:
    namespace = meta['namespace'].lower()
    filename = meta['path']

    df = pd.read_csv(filename, sep='\t')
    df = df.rename(columns={_: clean(_) for _ in df.columns})
    del df['gene_id']
    df = df.set_index('gene_name')

    df.to_sql('e_' + namespace, psql, if_exists='replace')

    doc = {
      'origin': filename,
      'namespace': namespace,
      'db': 'e_' + namespace,
      'tissues': list(df.columns[1:])
    }
    expre_meta.update({'namespace': namespace}, doc, True)

    logging.debug('Added {0} to the DB.'.format(namespace))
