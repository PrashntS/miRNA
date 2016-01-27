#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import os, os.path

from whoosh.index import create_in, open_dir

from miRNA import app
from miRNA.search.model import PolynucleotideSchema, NotIndexedException

class Indexer(object):
  def index_setup(collections):
    index_path = app.config.get('WHOOSH_INDEX')
    if not os.path.exists(index_path):
      os.mkdir(index_path)

    ix = create_in(index_path, schema = PolynucleotideSchema)
    writer = ix.writer()

    x = 0
    for collection in collections:
      docs = collection.objects
      for doc in docs:
        x += 1
        writer.add_document(**doc._repr)

    writer.commit()

    return {
      'indexed_doc_count': x,
    }

  def get_index():
    index_path = app.config.get('WHOOSH_INDEX')
    if not os.path.exists(index_path):
      raise NotIndexedException

    ix = open_dir(index_path)
    return ix
