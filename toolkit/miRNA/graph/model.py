#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import networkx as nx

from pydash import py_

from miRNA import zdb

graph = zdb.root.nxGraph

class Graph(object):

  def node_neighbor(node):
    """
    Returns the neighbours of the given node.
    """
    pass

class DepthLimitedVisit(object):
  def __init__(self, depth):
    self.visited = set()
    self.depth_limit = depth

  def depth_limited_visits(self, node, depth = 0):
    if depth == self.depth_limit:
      return self.visited

    neighbors = graph.predecessors(node) + graph.successors(node)

    for n_node in neighbors:
      if n_node not in self.visited:
        self.visited.add(n_node)
        self.depth_limited_visits(n_node, depth + 1)

  def ranked_visits(self, parameter):
    return py_.sort(self.visited, parameter)
