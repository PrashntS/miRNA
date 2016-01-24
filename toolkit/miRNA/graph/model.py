#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import networkx as nx

from miRNA.graph.store import miRNA_nodes, gene_nodes, in_edge, out_edge
from miRNA.polynucleotide.model import Gene, miRNA

class memGraph(object):
  """
  Provides an Abstraction over the Redis data store layer.
  This enables Edge Lookup, Neighbour lookup and Node Classes.
  """

  def __init__(self):
    pass

  def targets(node):
    """
    Returns targets of given node (miRNA).
    Args: node - miRNA
    Returns: List of touples
    """
    return out_edge[node]

  def host_of(node):
    """
    Returns miRNAs that are produced by node (gene).
    Args: node - gene
    Returns: List of touples
    """
    return out_edge[node]

  def targeted_by(node):
    """
    Returns the miRNAs that targets this node (gene).
    Args: node - gene
    Returns: List of touples
    """
    return in_edge[node]

  def source(node):
    """
    Returns the genes that produce this node (miRNA).
    Args: node - miRNA
    Returns: List of touples
    """
    return in_edge[node]

class Graph(object):
  def __init__(self, node_list):
    self.g = nx.DiGraph()
    self.g.add_nodes_from(Gene.objects())
