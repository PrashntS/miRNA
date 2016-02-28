#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import pandas as pd

from packrat import db

class ExpressionAtlas(object):
  """
  Provide access to ExpressionAtlas data for the given `namespace`.
  Namespaces are the Expression Atlas experiments that are available.

  Args:
    namespace (str): ExpressionAtlas Namespace. Default 'EMTAB2919'

  Ceavats:
    Access obj.tissues to list the tissues available.
  """

  def __init__(self, namespace=None, bulk=False):
    if namespace is None:
      namespace = 'EMTAB2919'
    self.bulk = bulk
    self.__init_db(namespace)

  def __init_db(self, namespace):
    meta_doc = db['expre_meta'].find_one({'namespace': namespace})
    if meta_doc is None:
      raise KeyError('Namespace {0} does not exists.'.format(namespace))
    self.meta_doc = meta_doc
    self.namespace = namespace
    self.collecn = db[meta_doc['db']]
    if self.bulk:
      self.df = pd.DataFrame(list(self.collecn.find()))

  @property
  def tissues(self):
    return self.meta_doc['fields']

  def __expr_level_single(self, node):
    doc = self.collecn.find_one({'gene_id': node})
    try:
      del doc['_id']
      del doc['gene_id']
    except TypeError:
      raise ValueError("Data for {0} is not available.".format(node))

    if self.tissue is not None:
      return float(doc[self.tissue])
    else:
      return {k: float(v) for k, v in doc.items()}

  def __expr_level_bulk(self, node):
    row = self.df.query("gene_id=='{0}'".format(node))

    if len(row) == 0:
      raise ValueError("Data for {0} is not available.".format(node))

    if self.tissue is not None:
      return float(row[self.tissue].values[0])
    else:
      return {k: float(row[k].values[0]) for k in self.tissues}

  def expr_level(self, node):
    if self.bulk:
      return self.__expr_level_bulk(node)
    else:
      return self.__expr_level_single(node)

  @property
  def tissue(self):
    if hasattr(self, '_tissue'):
      return self._tissue
    else:
      return None

  @tissue.setter
  def tissue(self, value):
    if value in self.tissues:
      self._tissue = value
    else:
      raise ValueError("{0} is not a valid tissue name.".format(value))

