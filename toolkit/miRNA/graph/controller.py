#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import networkx as nx

from pydash import py_
from flask_restful import Resource, reqparse

from miRNA.polynucleotide.model import Gene, miRNA, zdb

graph = zdb.root.nxGraph

class SubGraphController(Resource):
  def args(self):
    parser = reqparse.RequestParser()
    parser.add_argument('genes', type = str, action = 'append')
    parser.add_argument('mirna', type = str, action = 'append')
    return parser.parse_args()

  def get(self):
    swag = self.args()
    genes = self._gather(Gene, swag.get('genes'))
    mirna = self._gather(miRNA, swag.get('mirna'))

    return self._get(mirna, genes)

  def induce_subgraph(self, nodes):
    nbunch1 = []
    for node in nodes:
      nbunch1 += graph.successors(node)
      nbunch1 += graph.predecessors(node)

    nbunch2 = []
    for node in nbunch1:
      nbunch2 += graph.successors(node)
      nbunch2 += graph.predecessors(node)

    nbunch = py_.uniq(nbunch2)
    subgraph = graph.subgraph(nbunch)

    #: Rank the nodes, and eliminate them.

  def _gather(self, collection, arr):
    doc = []

    if not arr:
      return doc
    for sym in arr:
      try:
        doc.append(collection.objects.get(symbol = sym))
      except Exception:
        pass
    return doc
