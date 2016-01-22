#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import networkx as nx

from miRNA import rd
from miRNA.polynucleotide.model import Gene, miRNA

class Graph(object):
  def __init__(self, node_list):
    self.g = nx.DiGraph()
    self.g.add_nodes_from(Gene.objects())
