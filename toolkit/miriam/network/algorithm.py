#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import networkx as nx

from pydash import py_
from networkx.algorithms import isomorphism
from networkx.exception import NetworkXError


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


def pagerank(G, alpha=0.85, personalization=None,
             max_iter=100, tol=1.0e-6, nstart=None, weight='weight',
             dangling=None):
  """Return the PageRank of the nodes in the graph.

  Adapted from NetworkX

  PageRank computes a ranking of the nodes in the graph G based on
  the structure of the incoming links. It was originally designed as
  an algorithm to rank web pages.

  Parameters
  ----------
  G : graph
    A NetworkX graph.  Undirected graphs will be converted to a directed
    graph with two directed edges for each undirected edge.

  alpha : float, optional
    Damping parameter for PageRank, default=0.85.

  personalization: dict, optional
    The "personalization vector" consisting of a dictionary with a
    key for every graph node and nonzero personalization value for each node.
    By default, a uniform distribution is used.

  max_iter : integer, optional
    Maximum number of iterations in power method eigenvalue solver.

  tol : float, optional
    Error tolerance used to check convergence in power method solver.

  nstart : dictionary, optional
    Starting value of PageRank iteration for each node.

  weight : key, optional
    Edge data key to use as weight.  If None weights are set to 1.

  dangling: dict, optional
    The outedges to be assigned to any "dangling" nodes, i.e., nodes without
    any outedges. The dict key is the node the outedge points to and the dict
    value is the weight of that outedge. By default, dangling nodes are given
    outedges according to the personalization vector (uniform if not
    specified). This must be selected to result in an irreducible transition
    matrix (see notes under google_matrix). It may be common to have the
    dangling dict to be the same as the personalization dict.

  Returns
  -------
  pagerank : dictionary
     Dictionary of nodes with PageRank as value
  """
  if len(G) == 0:
    return {}

  if not G.is_directed():
    D = G.to_directed()
  else:
    D = G

  # Create a copy in (right) stochastic form
  W = nx.stochastic_graph(D, weight=weight)
  N = W.number_of_nodes()

  # Choose fixed starting vector if not given
  if nstart is None:
    x = dict.fromkeys(W, 1.0 / N)
  else:
    # Normalized nstart vector
    s = float(sum(nstart.values()))
    x = dict((k, v / s) for k, v in nstart.items())

  if personalization is None:
    # Assign uniform personalization vector if not given
    p = dict.fromkeys(W, 1.0 / N)
  else:
    missing = set(G) - set(personalization)
    if missing:
      raise NetworkXError('Personalization dictionary '
                          'must have a value for every node. '
                          'Missing nodes %s' % missing)
    s = float(sum(personalization.values()))
    p = dict((k, v / s) for k, v in personalization.items())

  if dangling is None:
    # Use personalization vector if dangling vector not specified
    dangling_weights = p
  else:
    missing = set(G) - set(dangling)
    if missing:
      raise NetworkXError('Dangling node dictionary '
                          'must have a value for every node. '
                          'Missing nodes %s' % missing)
    s = float(sum(dangling.values()))
    dangling_weights = dict((k, v/s) for k, v in dangling.items())
  dangling_nodes = [n for n in W if W.out_degree(n, weight=weight) == 0.0]

  # power iteration: make up to max_iter iterations
  for _ in range(max_iter):
    xlast = x
    x = dict.fromkeys(xlast.keys(), 0)
    danglesum = alpha * sum(xlast[n] for n in dangling_nodes)
    for n in x:
      # this matrix multiply looks odd because it is
      # doing a left multiply x^T=xlast^T*W
      for nbr in W[n]:
        x[nbr] += alpha * xlast[n] * W[n][nbr][weight]
        x[n] += danglesum * dangling_weights[n] + (1.0 - alpha) * p[n]
    # check convergence, l1 norm
    err = sum([abs(x[n] - xlast[n]) for n in x])
    if err < N*tol:
      return x
  raise NetworkXError('pagerank: power iteration failed to converge '
                      'in %d iterations.' % max_iter)

