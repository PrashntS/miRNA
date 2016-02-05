#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import networkx as nx

from pydash import py_

from miRNA import memcache
from miRNA.graph.model import graph
from miRNA.graph.triads import Motif

class Ranking(object):
  def _rank_nbunch(self, nbunch):
    raise NotImplementedError

  def _cmp(self, n1, n2):
    raise NotImplementedError

class DegreeRanking(Ranking):
  def __init__(self, ibunch):
    self.ibunch = ibunch
    self.MIRNAINX = 2
    self.GENEOUTX = 20

  def __node_value(self, node):
    nkind = graph.node[node]['kind']
    if nkind == 'GEN':
      i_d = graph.in_degree(node)
      o_d = graph.out_degree(node) * self.GENEOUTX
    elif nkind == 'MIR':
      i_d = graph.in_degree(node) * self.MIRNAINX
      o_d = graph.out_degree(node)
    deg = i_d + o_d
    return deg

  def _organic_rank_nbunch(self, nbunch):
    return py_.sort(nbunch, key=self.__node_value, reverse=True)

@memcache.cached()
def motif_score_reference():
  mtf = Motif(graph)
  return {_: len(mtf.find_all(_)) for _ in mtf.kinds.keys()}
