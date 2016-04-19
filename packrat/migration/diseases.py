#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
import logging
import pandas as pd

from packrat import db
from miriam import psql
from packrat import catalogue

dis_meta = db['diseases_meta']

def routine():
  #: Register Fields in the Expression Metadata
  for meta in catalogue['disease_network']:
    namespace = meta['namespace']
    filename = meta['path']

    df = pd.read_csv(filename, sep='\t')
    del df['sourceId']
    del df['NofSnps']
    del df['NofPmids']
    del df['geneId']
    del df['description']

    df.to_sql('d_' + namespace, psql, if_exists='replace')

    doc = {
      'origin': filename,
      'namespace': namespace,
      'db': 'd_' + namespace,
    }
    dis_meta.update({'namespace': namespace}, doc, True)

    logging.debug('Added {0} to the DB.'.format(namespace))
