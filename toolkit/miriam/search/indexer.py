#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import os, os.path

from whoosh.index import create_in, open_dir

from miriam import app, logger
from miriam.search.model import PolynucleotideSchema, NotIndexedException

class Indexer(object):
  @staticmethod
  def index(doc_sets):
    index_path = app.config.get('WHOOSH_INDEX')
    if not os.path.exists(index_path):
      os.mkdir(index_path)

    ix = create_in(index_path, schema = PolynucleotideSchema)
    writer = ix.writer()

    coll_count = 0
    for collection, normaliser in doc_sets:
      coll_count += 1
      logger.info("Indexing Collection #{0}.".format(coll_count))

      count = 0
      for doc in collection:
        count += 1
        writer.add_document(**normaliser(doc))
      logger.info("Indexed {0} documents.".format(count))

    writer.commit()
    logger.info("Index Commited.")

  @staticmethod
  def get_index():
    index_path = app.config.get('WHOOSH_INDEX')
    if not os.path.exists(index_path):
      raise NotIndexedException

    ix = open_dir(index_path)
    return ix
