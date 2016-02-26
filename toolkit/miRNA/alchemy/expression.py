#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

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

  def __init__(self, namespace=None):
    if namespace is None:
      namespace = 'EMTAB2919'
    self.__init_db(namespace)

  def __init_db(self, namespace):
    meta_doc = db['expre_meta'].find_one({'namespace': namespace})
    if meta_doc is None:
      raise KeyError('Namespace {0} does not exists.'.format(namespace))
    self.meta_doc = meta_doc
    self.namespace = namespace
    self.collecn = db[meta_doc['db']]

  @property
  def tissues(self):
    return self.meta_doc['fields']

  def expr_level(self, node):
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

  def nbunch(self, nbunch):
    """
    Generate stats about the Genes that aren't present in this namespace.
    Use to filter the candidate genes, etc.

    Args:
      nbunch (list): The gene ids of the staged genes.
    """
    out = {
      'unavailable': [],
      'available': [],
    }
    for node in nbunch:
      try:
        self.expr_level(node)
      except ValueError:
        out['unavailable'].append(node)
      else:
        out['available'].append(node)
    out['stats'] = {
      'l_available': len(out['available']),
      'l_unavailable': len(out['unavailable']),
      'p_available': len(out['available']) / len(nbunch) * 100,
      'p_unavailable': len(out['unavailable']) / len(nbunch) * 100
    }
    return out

class ExpressionStats(object):
  def __init__(self, namespace):
    pass
