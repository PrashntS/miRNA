#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
import requests
import logging

from huey import RedisHuey
from pymongo import MongoClient
from ZODB import DB as ZDB
from ZEO.ClientStorage import ClientStorage as ZeoClientStorage

from packrat.config import HUEY, MONGO, ZEOCONF
from packrat.alchemy.ensembl import ensembl_sequence, ensembl_gene_id
from packrat.alchemy.ncbi import ncbi_search_id, ncbi_get_summary

huey    = RedisHuey(**HUEY)
moncli  = MongoClient(**MONGO)
db      = moncli['packrat']

storage = ZeoClientStorage(ZEOCONF)
zdb     = ZDB(storage).open()

@huey.task(retries=10, retry_delay=10)
def spawn_gene_dat(gene_id):
  tb = db['ncbi_gene_docs']

  if not tb.find({'gene_id': gene_id}).count() > 0:
    try:
      ncbi_id = ncbi_search_id(gene_id)['eid']
    except AttributeError:
      tb = db['stats_missed_genes']
      tb.insert({
        'gene_id': gene_id,
      })
      return
    ncbi_doc = ncbi_get_summary(ncbi_id)
    doc = ncbi_doc['doc']
    doc['gene_id'] = gene_id
    tb.insert(doc)

  logging.info("Gene Done: {0}".format(gene_id))

@huey.task(retries=10, retry_delay=10)
def spawn_ensembl_dat(gene_id):
  tb = db['ensembl_seq']

  query = {
    'fasta.error': {
      '$exists': False
    },
    'gene_id': gene_id
  }

  if not tb.find(query).count() > 0:
    ensebl_id = ensembl_gene_id(gene_id)['doc']['emblid']
    embl_dat = ensembl_sequence(ensebl_id)
    doc = embl_dat['doc']
    doc['gene_id'] = gene_id
    tb.update({'gene_id': gene_id}, doc, True)

  logging.info("Sequences Done: {0}".format(gene_id))
