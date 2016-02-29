#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import networkx as nx

from pydash import py_
from flask_restful import Resource, reqparse

from miriam.graph import g
from miriam.graph.model import depth_limited_nodes, GraphKit

class SubGraphController(Resource):
  def args(self):
    parser = reqparse.RequestParser()
    parser.add_argument('genes', type = str, action = 'append')
    parser.add_argument('mirna', type = str, action = 'append')
    return parser.parse_args()

  def get(self):
    swag = self.args()
    genes = swag.get('genes')
    mirna = swag.get('mirna')

    return self.induce_subgraph(genes)

  def induce_subgraph(self, nodes):
    subgraph = g.g.subgraph(depth_limited_nodes(nodes, g, 1))
    sub = GraphKit(subgraph)
    return {
      'genes_store': sub.genes,
      'miRNA_store': sub.mirnas,
      'target_list': [_ for _ in sub.g.edges(data=True) if _[2]['kind']=='M>G'],
      'host_list': [_ for _ in sub.g.edges(data=True) if _[2]['kind']=='G>M'],
    }
