#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import networkx as nx

from pydash import py_
from networkx.algorithms import isomorphism

class Motif(object):
  def __init__(self, g):
    self.g = g
    self.__init_graph_kinds()

  def __g_gen(self, k, m):
    g = nx.DiGraph()
    g.add_node('G', kind='GEN')
    g.add_node('M1', kind='MIR')
    if k[0] == 'T':
      g.add_node('M2', kind='MIR')
    g.add_edges_from(m)
    return self.__generate_matcher(g)

  def __init_graph_kinds(self):
    self.kinds = {
      'D1': [('G', 'M1'), ('M1', 'G')],
      'T2': [('G', 'M1'), ('M1', 'G'), ('G', 'M2'), ('M2', 'G')],
      'T3': [('G', 'M1'), ('M1', 'G'), ('G', 'M2')],
      'T4': [('G', 'M1'), ('M1', 'G'), ('M2', 'G')],
      'T6': [('M1', 'G'), ('G', 'M2')],
      'T7': [('G', 'M1'), ('G', 'M2')],
    }
    self.no_order = ['T2', 'T7']
    self.g_k = {k: self.__g_gen(k, m) for k, m in self.kinds.items()}

  def __generate_matcher(self, g2):
    node_match = lambda x, y: x['kind'] == y['kind']
    return isomorphism.DiGraphMatcher(self.g, g2, node_match=node_match)

  def _iter_kind(self, kind):
    motifs = self.g_k[kind].subgraph_isomorphisms_iter()
    for motif in motifs:
      yield motif

  @staticmethod
  def __duplicates(v, *args):
    nodes = list(v.keys())
    nodes.sort()
    return "".join(nodes)

  @staticmethod
  def __post_process(dat):
    return [{v: k for k, v in d.items()} for d in dat]

  def find_all(self, kind):
    out = [_ for _ in self._iter_kind(kind)]
    if kind in self.no_order:
      out_pre = py_.uniq(out, callback=Motif.__duplicates)
    else:
      out_pre = out
    return Motif.__post_process(out_pre)
