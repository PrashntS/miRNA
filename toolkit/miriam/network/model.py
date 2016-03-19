#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import networkx as nx

from packrat.migration import graph as graph_store

class GraphKit(object):
  """
  Abstraction over the networkx graph.

  API:
    - Return list of miRNAs: GraphKit.mirnas
    - Return list of genes: GraphKit.genes
    - Return the host genes of miRNA, or miRNA the gene is host of:
      GraphKit.host
    - Return the targets of miRNA, or the miRNAs that target the gene:
      GraphKit.target
    - Return the transcript count of the miRNA Host, or Gene:
      GraphKit.transc_count
  """

  def __init__(self, graph=None):
    if graph is not None:
      self.g = graph
    else:
      try:
        self.g = graph_store.get()
      except Exception:
        raise RuntimeError("Graph data not persistent. Migration Required.")

  @property
  def mirnas(self):
    return [k for k, v in self.g.node.items() if v['kind'] == 'MIR']

  @property
  def genes(self):
    return [k for k, v in self.g.node.items() if not v['kind'] == 'MIR']

  def host(self, node, *a, **kwa):
    """
    Return the Host Gene, if `node` is miRNA, or, the miRNAs produced by the
    gene if `node` is a Gene.

    Args:
      node (str): Node Name

    Example:
      >>> g.host('MCM7') # is a gene
      ['hsa-miR-106b-5p', 'hsa-miR-93-5p', ...]
    """

    if self.g.node[node]['kind'] == 'MIR':
      return self.g.predecessors(node)
    elif self.g.node[node]['kind'] == 'GEN':
      return self.g.successors(node)
    else:
      raise ValueError("Node is unsupported kind.")

  def target(self, node, *a, **kwa):
    """
    Return the target genes, if `node` is miRNA, or, the miRNAs that target this
    gene if `node` is a Gene.

    Args:
      node (str): Node Name
    """

    if self.g.node[node]['kind'] == 'MIR':
      return self.g.successors(node)
    elif self.g.node[node]['kind'] == 'GEN':
      return self.g.predecessors(node)
    else:
      raise ValueError("Node is unsupported kind.")

