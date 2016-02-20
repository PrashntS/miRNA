#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
import requests
import logging

from huey import RedisHuey
from pymongo import MongoClient

from packrat.config import HUEY, MONGO
from packrat.alchemy.ensembl import ensembl_sequence
from packrat.alchemy.ncbi import ncbi_search_id, ncbi_get_summary

huey = RedisHuey(**HUEY)
moncli = MongoClient(**MONGO)
db = moncli['packrat']

@huey.task(retries=10, retry_delay=10)
def spawn_gene_dat(gene_id):
  tb = db['ncbi_gene_docs']

  if not tb.find({'gene_id': gene_id}).count() > 0:
    ncbi_id = ncbi_search_id(gene_id)['eid']
    ncbi_doc = ncbi_get_summary(ncbi_id)
    doc = ncbi_doc['doc']
    doc['gene_id'] = gene_id
    tb.insert(doc)
    spawn_ensembl_dat(gene_id, doc['ensemblid'])

  logging.info("Gene Done: {0}".format(gene_id))

@huey.task(retries=10, retry_delay=10)
def spawn_ensembl_dat(gene_id, ensebl_id):
  tb = db['ensembl_seq']

  if not tb.find({'gene_id': gene_id}).count() > 0:
    embl_dat = ensembl_sequence(ensebl_id)
    doc = embl_dat['doc']
    doc['gene_id'] = gene_id
    tb.insert(doc)

  logging.info("Sequences Done: {0}".format(gene_id))

