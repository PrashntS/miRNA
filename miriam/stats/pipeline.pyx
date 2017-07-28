# MiRiam
import pandas as pd
import numpy as np
import numpy.linalg
import networkx as nx
import functools
import itertools
import math
import os

from multiprocessing import Pool
from pydash import py_
from math import exp
from operator import mul
from matplotlib import pyplot as plt

from miriam import psql, db, config
from miriam.logger import logger
from miriam.network import g
from miriam.network.model import GraphKit
from miriam.network.algorithm import Motif
from packrat.migration.graph import function_classes
from miriam.alchemy.utils import mproperty
from miriam.alchemy.rank import Frame


cdef int CONCURRENCY = 3

cdef float R = 8.314
cdef float T = 303
cdef float RTI = -1.0 / (R * T)
cdef float e = exp(1)


def unit_scale(x):
  L1 = numpy.linalg.norm(x, ord=1)
  if L1 > 0:
    return x / L1
  else:
    return np.zeros_like(x)


cdef float SPT_A = 20
cdef float SPT_B = 19 * 2

cdef float scale_spt(int x):
  cdef float n, d
  n = (SPT_A * SPT_B * x)
  d = (x ** 2) + (SPT_A ** 2)
  return 1 + (n / d)


def step_keq(r):
  '''Calculate K equivalent.'''
  cdef float dg = r['dg']
  cdef float e_gene = math.log(r['exp_gene'] + 1)
  cdef float e_mirn = math.log(r['exp_host'] + 1)
  try:
    return (e ** (RTI * dg)) * (e_mirn / e_gene)
  except ZeroDivisionError:
    return None

cpdef float step_deg(r):
  cdef int dm = r['mirna']
  cdef int dg = r['gene']
  return dg / dm



class Pipeline(object):
  def __init__(self, tissue):
    self.frame = Frame(tissue)

  def _chunks(self, frame, chunk_count, method):
    size = len(frame)
    step_size = size // chunk_count
    step_x = list(range(0, size, step_size))
    step_y = step_x[1:]
    if len(step_x) > chunk_count:
      # account for last remaining chunk
      step_y.append(size)

    steps = zip(step_x, step_y)
    for x, y in steps:
      yield frame[x:y], method

  def _apply(self, args):
    dataframe, method = args
    return dataframe.apply(method, axis=1)

  def _get_column(self, on, method):
    pool = Pool(processes=CONCURRENCY)
    res = pool.map(self._apply, self._chunks(on, CONCURRENCY, method))
    pool.close()
    return pd.concat(res)

  def _fn_keq(self, r):
    '''Calculate K equivalent.'''
    cdef float dg = r['dg']
    cdef float e_gene = math.log(r['exp_gene'] + 1)
    cdef float e_mirn = math.log(r['exp_host'] + 1)
    try:
      return (e ** (RTI * dg)) * (e_mirn / e_gene)
    except ZeroDivisionError:
      return None

  def _fn_deg(self, r):
    '''Calculate degree correction.'''
    dm = self._deg_graph.deg(r['mirna'])
    dg = self._deg_graph.deg(r['gene'])
    return dg / dm

  def _fn_ont(self, r):
    '''Calculate ontology values.'''
    scs = ['ont_fnc', 'ont_pharmgkb', 'ont_kegg', 'ont_smpdb', 'ont_pid']
    score = 0x0
    for ont in scs:
      rt = ont + '_x'
      lt = ont + '_y'
      ont = int(r[rt], 16) & int(r[lt], 16)
      score += str(bin(ont)).count('1')
    score += r['gene'] == r['host']
    return scale_spt(score)

  def _combine_scores(self, frame, columns):
    pass

  def as_graph(self, frame):
    logger.debug('[GraphKit] Begin')
    g = nx.DiGraph()
    g.add_edges_from(frame.loc[:,('mirna', 'gene')].values)
    g.add_edges_from(frame.loc[:,('host', 'mirna')].values)
    gk = GraphKit(g)
    logger.debug('[GraphKit] End')
    return gk

  def as_nx_graph(self, frame):
    logger.debug('[NxGraph] Begin')
    g = nx.DiGraph()
    g.add_weighted_edges_from((frame
        .loc[:,('mirna', 'gene', 'score')]
        .values))
    logger.debug('[NxGraph] End')
    return g

  @mproperty
  def nx_graph(self):
    return self.as_nx_graph(self.stack)

  @mproperty
  def stack(self):
    '''Ranking Stacks'''
    raise NotImplemented

  def plot_line(self, frame, col):
    ''''''
    dat = frame[col].plot(logy=True)
    plt.show()

  def plot_hist(self, frame, col):
    '''Plots Histogram'''
    dat = frame[col].tolist()
    dat.sort()
    log = lambda x: math.log(x) if x > 0 else None
    datexp = map(log, dat)
    datmod = list(filter(lambda x: x, datexp))
    plt.hist(datmod, bins=75)
    plt.show()

  def _node_rank(self, kind, nodes):
    ranked = nx.degree_centrality(self.nx_graph)
    if kind is 'mirna':
      test = lambda x: 'hsa-' in x
    else:
      test = lambda x: 'hsa-' not in x

    nodes = dict([(_, ranked[_]) for _ in ranked if test(_)])

    scores = [(_, nodes.get(_, None)) for _ in nodes]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

  def ontology_score(self, kind):
    genes = (self
        .stack
        .drop_duplicates('host')
        .loc[:,('host', 'ont_fnc_x', 'ont_pharmgkb_x', 'ont_kegg_x', 'ont_smpdb_x', 'ont_pid_x')]
        .set_index('host')
        .to_dict())

    dim_pivot = max(genes[kind], key=lambda x: int(genes[kind][x], 16))
    val = genes[kind][dim_pivot]

    to_vector = lambda x: np.array([int(_) for _ in bin(int(x, 16))[2:]])

    val_dim = np.zeros_like(to_vector(val), dtype='float64')

    out = val_dim.copy()

    for gene, score in self.genes:
      if gene in genes[kind]:
        vec = to_vector(genes[kind][gene]) * score
        vec.resize(len(out))
        out += vec
    return out

  @mproperty
  def mirnas(self):
    return self._node_rank('mirna', g.mirnas)

  @mproperty
  def genes(self):
    return self._node_rank('gene', g.genes)

  @property
  def graph(self):
    return self.as_graph(self.stack)

  @mproperty
  def motifs(self):
    formats = {
      'D1': "{M1} ⇌ {G}",
      'T2': "{M1} ⇌ {G} ⇌ {M2}",
      'T3': "{M1} ⇌ {G} → {M2}",
      'T4': "{M1} ⇌ {G} ← {M2}",
      'T6': "{M1} → {G} → {M2}",
      'T7': "{M1} ← {G} → {M2}"
    }
    mir_scores = dict(self.mirnas)
    gene_scores = dict(self.genes)

    def motif_fmt(motif, kind):
      score = 0
      for k, v in motif.items():
        if 'M' in k:
          score += mir_scores.get(v, 0)
        else:
          score += gene_scores.get(v, 0)
      return formats[kind].format(**motif), score

    return {k: [motif_fmt(m, k) for m in v] for k, v in self.graph.motif.items()}

  def report(self):
    genes = self.genes
    genes.sort(key=lambda x: x[0])

    mirnas = self.mirnas
    mirnas.sort(key=lambda x: x[0])

    # as_list = lambda *x: [j for i in x for j in i]
    # motifs_mapped = dict(as_list(*self.motifs.values()))
    # motifs = [motifs_mapped.get(_, 0.0) for _ in g.motif_hash]

    fmt_interaction = lambda x: ('{0} {1}'.format(x[0], x[1]), x[2])
    interactions = self.stack.loc[:, ('mirna', 'host', self.col_ranks)].values
    interactions_formatted = dict(map(fmt_interaction, interactions))

    interactions = [interactions_formatted.get(_, 0.0) for _ in g.interaction_hash]

    return {
      'tissue': self.frame.tissue.id,
      'genes': [x[1] for x in genes],
      'mirnas': [x[1] for x in mirnas],
      # 'motifs': motifs,
      'interactions': interactions,
    }

  @mproperty
  def diseases(self):
    flow_graph = nx.DiGraph()
    flow_graph.add_weighted_edges_from((self
        .stack
        .loc[:,('mirna', 'gene', 's_norm')]
        .values))
    flow_graph.add_weighted_edges_from((self
        .frame
        .diseases
        .loc[:, ('gene', 'diseaseId', 'score')]
        .values))

    diseases = self.frame.diseases.diseaseId.unique()
    mirnas = self.stack.mirna.unique()

    flow_graph.add_weighted_edges_from([('source', _, 1) for _ in mirnas])
    flow_graph.add_weighted_edges_from([(_, 'sink', 1) for _ in diseases])

    _, ranks = nx.maximum_flow(flow_graph, 'source', 'sink', capacity='weight')

    diseases_ranked = [(_, ranks[_]['sink']) for _ in diseases]
    diseases_ranked.sort(key=lambda x: x[1], reverse=True)
    return diseases_ranked


class Score_K_O_D(Pipeline):
  '''Score in KOD order.
  Calculate the score in following order:
    1. K equivalent (thermodynamics)
    2. Ontology
    3. Degree Score
  Thresholds applied at stage 2.
  '''

  @mproperty
  def stack(self):
    cached_file = os.path.join(config.pickle_dir, '{}.pkl'.format(self.frame.tissue.id))
    frame = self.frame.filtered
    self._deg_graph = self.as_graph(frame)

    try:
      return pd.read_pickle(cached_file)
    except FileNotFoundError:
      pass

    frame['s_keq'] = self._get_column(frame, self._fn_keq)
    frame['s_deg'] = self._get_column(frame, self._fn_deg)
    frame['s_ont'] = self._get_column(frame, self._fn_ont)

    frame['score'] = frame['s_keq'] * frame['s_ont'] * frame['s_ont']
    sframe = frame.sort_values('score', ascending=False)
    sframe.index = range(1, len(sframe) + 1)

    sframe.to_pickle(cached_file)

    return sframe
