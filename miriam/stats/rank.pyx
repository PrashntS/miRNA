#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import pandas as pd
import numpy as np
import networkx as nx
import functools
import itertools
import math

from multiprocessing import Pool
from pydash import py_
from math import exp
from operator import mul
from matplotlib import pyplot as plt

from miriam import psql, db
from miriam.logger import logger
from miriam.network import g
from miriam.network.model import GraphKit
from packrat.migration.graph import function_classes
from miriam.alchemy.utils import mproperty
from miriam.alchemy.rank import Tissue


cdef float R = 8.314
cdef float T = 303
cdef float RTI = -1.0 / (R * T)
cdef float e = exp(1)

class Ranking(object):
  def __init__(self, tissue, **kwa):
    # Thresholds
    self.th_ps2 = kwa.get('th_ps2', 1)
    self.th_ps3 = kwa.get('th_ps3', 1)
    self.__proc = kwa.get('__proc', 3)

    self.resetup = True

    self.tissue = tissue
    self.degcache = {}
    self.__preinit()

  def __preinit(self):
    logger.debug('Preinit - Begin Read NW')
    self.__ntwkdg = pd.read_sql_table('ntwkdg', psql)
    logger.debug('Preinit - Begin Read MR')
    self.__mirna  = pd.read_sql_table('mirn', psql)
    logger.debug('Preinit - Begin Read EXP')
    self.exp_dat = self.tissue.expression
    logger.debug('Preinit - Begin Read FNCLS')
    self.fncls = pd.read_sql_query(
      'select symbol, functional_cls from gene',
      psql)

  def __do_merge(self):
    """Return Merged Data Segments

    [Caveates] Returned Columns:
      ['mirna', 'gene', 'dg', 'exp_tar', 'host', 'exp_mir']
        0        1       2     3          4       5
    """
    #: Join Target Gene Expressions
    p1 = self.__ntwkdg.merge(self.exp_dat, left_on='gene', right_on='gene_name')
    del p1['gene_name']
    p1 = p1.rename(columns={self.tissue: 'exp_tar'})

    #: Join MiRNA's host genes
    p2 = p1.merge(self.__mirna, left_on='mirna', right_on='symbol')
    del p2['symbol']

    p3 = p2.merge(self.exp_dat, left_on='host', right_on='gene_name')
    del p3['gene_name']
    p3 = p3.rename(columns={self.tissue: 'exp_mir'})

    del p1
    del p2
    return p3

  def __degree(self, x):
    try:
      return self.degcache[x]
    except KeyError:
      deg = self.g_p2.degree(x)
      self.degcache[x] = deg
      return deg

  def _f_r1(self, row):
    cdef float dg = row[2]
    cdef float eg = row[3]
    cdef float em = row[5]
    try:
      return (e ** (RTI * dg)) * (em / eg)
    except ZeroDivisionError:
      return None

  def _f_r2(self, row):
    cdef int dm = self.__degree(row[0])
    cdef int dg = self.__degree(row[1])
    cdef float r1 = row[6]

    return r1 * dg / dm

  def __setup_ground(self):
    """Adds First Ranking to the DataFrame.
    [Caveates] Added column: `r1`, index: 6
    """
    logger.debug('Setup Ground - Begin Merge')
    gd = self.__do_merge()

    #: Calculate keq.

    logger.debug('Setup Ground - Apply 1')
    gd['r1'] = self.__coroutine_apply('_f_r1', gd)

    logger.debug('Setup Ground - Sort')
    gd_p1 = gd.sort_values('r1', ascending=False)
    gd_p1.index = range(1, len(gd_p1) + 1)
    self.gd_p1 = gd_p1
    self.resetup = False

  def __get_deg_rank(self):
    pd.options.mode.chained_assignment = None
    logger.debug('Deg Rank - Init Q')
    self.gd_p2 = self.gd_p1.query('{0} < r1 < {1}'.format(exp(-4), exp(4)))
    self.g_p2 = nx.from_edgelist(self.gd_p2.loc[:,('mirna', 'gene')].values,
        create_using=nx.DiGraph())

    logger.debug('Deg Rank - Apply')
    self.gd_p2['r2'] = self.__coroutine_apply('_f_r2', self.gd_p2)

    logger.debug('Deg Rank - Sort')
    gd_p3 = self.gd_p2.sort_values('r2', ascending=False)
    gd_p3.index = range(1, len(gd_p3) + 1)
    gd_p3 = gd_p3.query('r2 > 0')
    return gd_p3

  def __srange(self, lim, step, chunks):
    opts = [[i, i+step] for i in range(0, lim, step)]
    a, _ = opts.pop()
    opts.append([a, lim])

    return [opts[i:i+chunks] for i in range(0, len(opts), chunks)]

  def _process_chunk(self, dat):
    func = getattr(self, dat[0])
    return dat[1].apply(func, axis=1)

  def __coroutine_apply(self, func, frame):
    passes = []
    pool = Pool(processes=self.__proc)

    frame_len = int(len(frame) / self.__proc)

    for cx in self.__srange(len(frame), frame_len, self.__proc):
      chunks = [[func, frame[_[0]:_[1]]] for _ in cx]
      res = pool.map(self._process_chunk, chunks)
      passes.append(res)

    pool.close()
    return pd.concat(py_.flatten(passes))

  def patch_ranks(self, **kwa):
    if self.resetup is True:
      self.__setup_ground()

    self.th_ps2 = kwa.get('threshold_ground', self.th_ps2)
    self.th_ps3 = kwa.get('threshold_degree', self.th_ps3)
    self.__ranks = self.__get_deg_rank()

  @property
  def ranks(self):
    if self.resetup is True:
      self.patch_ranks()
    return self.__ranks

  def functional_impact(self, zipped=True, sorted=True):
    merged = self.ranks.merge(self.fncls,
        left_on='gene',
        right_on='symbol',
        how='left')

    del merged['symbol']

    def _function(x):
      vector_s = x['functional_cls'][1:-1].split(',')
      return list(map(lambda _: x['r2'] * int(_), vector_s))

    dat = merged.apply(_function, axis=1)
    impacts = list(map(sum, zip(*dat)))

    if zipped:
      to_return = list(zip(function_classes(), impacts))
      if sorted:
        to_return.sort(key=lambda x: x[1], reverse=True)
      return to_return
    else:
      return impacts

  def functional_bumps(self, ranks):
    logger.debug('Merging Vectors - Init')
    merged = ranks.merge(self.fncls,
        left_on='gene',
        right_on='symbol',
        how='left')

    del merged['symbol']

    merged = merged.merge(self.fncls,
        left_on='host',
        right_on='symbol',
        how='left')

    del merged['symbol']
    logger.debug('Merging Vectors - Done')

    def _function(x):
      vector_s = x['functional_cls_x'][1:-1].split(',')
      vector_t = x['functional_cls_y'][1:-1].split(',')
      pairs = zip(vector_s, vector_t)
      expectation = sum(map(lambda y: int(y[0]) * int(y[1]), pairs))
      if x['gene'] == x['host']:
        expectation += 1

      return x['r2'] * exp(expectation)

    logger.debug('Score Rearrangement - Init')
    merged['r3'] = merged.apply(_function, axis=1)
    logger.debug('Score Rearrangement - Sort')
    rank_adapted = merged.sort_values('r3', ascending=False)
    logger.debug('Score Rearrangement - Re-index')
    rank_adapted.index = range(1, len(rank_adapted) + 1)

    return rank_adapted

  @property
  def report(self):
    if self.resetup is True:
      self.patch_ranks()

    uniq_mir_p2 = len(self.gd_p2['mirna'].value_counts())
    uniq_mir_p3 = len(self.ranks['mirna'].value_counts())

    uniq_gen_p2 = len(self.gd_p2['gene'].value_counts())
    uniq_gen_p3 = len(self.ranks['gene'].value_counts())

    return {
      'pass_one': {
        'unique_mirnas': uniq_mir_p2,
        'unique_genes': uniq_gen_p2,
        'total_interactions': len(self.gd_p2),
      },
      'pass_two': {
        'unique_mirnas': uniq_mir_p3,
        'unique_genes': uniq_gen_p3,
        'total_interactions': len(self.ranks),
      },
    }

  def graphify(self, slice=100, noslice=True):
    """Return a NetworkX graph of the rankbunch.

    Args:
      slice: Valid Values are:
        - (int x) Slices the rank as rank[:x]
        - (list [x, y]) Slices the ranks as rank[x, y]

    [Caveates]
      rankbunch: Expects a Pandas dataframe slice having compatible columns.
        'mirna', 'gene', 'dg', 'exp_tar', 'host', 'exp_mir', 'r1', 'r2'
         0        1       2     3          4       5          6     7
    """
    # Generate MiRNA -> Gene Links with weights `r2`
    # Generate Host --> MiRNA Links with weights `exp_mir`
    if noslice is False:
      if type(slice) is int:
        x, y = 0, slice
      elif type(slice) in [list, tuple]:
        x, y = slice
      else:
        raise ValueError("`slice` is invalid")

      rankbunch = self.ranks[x:y]
    else:
      rankbunch = self.ranks

    g = nx.DiGraph()
    g.add_weighted_edges_from(rankbunch.loc[:,('mirna', 'gene', 'r2')].values)
    g.add_weighted_edges_from(rankbunch.loc[:,('host', 'mirna', 'exp_mir')].values)

    for i, j in [['MIR', 'mirna'], ['GEN', 'gene'], ['GEN', 'host']]:
      nx.set_node_attributes(g, 'kind', {v: i for v in rankbunch[j].values})

    self.__graph = GraphKit(g)
    return self.__graph

  @property
  def graph(self):
    try:
      return self.__graph
    except AttributeError:
      return self.graphify()

  def __node_ranks(self, kind):
    ranks = self.ranks
    if kind == 'mirna':
      nodes = g.mirnas
    elif kind == 'gene':
      nodes = g.genes
    else:
      raise ValueError
    score = lambda x: ranks.loc[ranks[kind] == x]['r2'].sum()
    return list(map(score, nodes))

  @property
  def mirnas(self):
    return self.__node_ranks('mirna')

  @property
  def genes(self):
    return self.__node_ranks('gene')


class Frame(object):
  def __init__(self, tissue):
    if type(tissue) is str:
      tissue = Tissue(tissue)
    self.tissue = tissue

  @mproperty
  def ontology(self):
    query = 'select symbol, functional_cls from gene'
    data  = pd.read_sql_query(query, psql)
    return data

  @mproperty
  def network(self):
    '''Return network edge'''
    logger.debug('[Frames] Reading NW DG')
    ntwkdg = pd.read_sql_table('ntwkdg', psql)
    mirnas = pd.read_sql_table('mirn', psql)
    merged = ntwkdg.merge(mirnas, left_on='mirna', right_on='symbol')
    del merged['symbol']
    merged = merged[['mirna', 'gene', 'host', 'dg']]
    return merged

  @mproperty
  def merged(self):
    '''Merge Tissue Expression Values with the Network'''
    logger.debug('[Frames] Merging expression with NW')
    merge_target = self.network.merge(
      self.tissue.expression,
      left_on='gene',
      right_on='gene_name')
    del merge_target['gene_name']
    merge_target = merge_target.rename(columns={
      self.tissue.tissue_id: 'exp_gene'
    })
    merge_host = merge_target.merge(
      self.tissue.expression,
      left_on='host',
      right_on='gene_name')
    del merge_host['gene_name']
    merge_host = merge_host.rename(columns={self.tissue.tissue_id: 'exp_host'})

    logger.debug('[Frames] Merging ontology')
    merge_ontology_gene = merge_host.merge(self.ontology,
      left_on='gene',
      right_on='symbol')
    del merge_ontology_gene['symbol']
    merge_ontology_gene = merge_ontology_gene.rename(columns={
      'functional_cls': 'ont_gene'
    })
    merge_ontology_host = merge_ontology_gene.merge(self.ontology,
      left_on='host',
      right_on='symbol')
    del merge_ontology_host['symbol']
    merge_ontology_host = merge_ontology_host.rename(columns={
      'functional_cls': 'ont_host'
    })

    return merge_ontology_host


class Pipeline(object):
  '''Ranking Stages - Modular Pipeline'''
  col_fn_deg = None
  col_fn_ont = None
  col_ranks  = None
  proc = 3

  def __init__(self, tissue):
    self.frame = Frame(tissue)

  def _chunks(self, frame, method):
    lim  = len(frame)
    step = lim // self.proc
    step_x = list(range(0, lim, step))
    step_y = step_x[1:]
    if len(step_x) > self.proc:
      step_y[-1] = lim
    else:
      step_y.append(lim)
    steps  = zip(step_x, step_y)
    for step in steps:
      yield frame[step[0]:step[1]], method

  def _apply(self, pair):
    return pair[0].apply(pair[1], axis=1)

  def _get_column(self, on, method):
    pool = Pool(processes=self.proc)
    passes = []

    res = pool.map(self._apply, self._chunks(on, method))
    pool.close()
    return pd.concat(res)

  def _fn_keq(self, r):
    '''Calculate K equivalent.'''
    cdef float dg = r['dg']
    cdef float e_gene = r['exp_gene']
    cdef float e_mirn = r['exp_host']
    try:
      return (e ** (RTI * dg)) * (e_mirn / e_gene)
    except ZeroDivisionError:
      return None

  def _fn_deg(self, r):
    '''Calculate degree correction.'''
    dm = self.__deg_graph__.deg(r['mirna'])
    dg = self.__deg_graph__.deg(r['gene'])
    try:
      score_prev = r[self.col_fn_deg]
    except KeyError:
      score_prev = 1
    return score_prev * (dg / dm)

  def _fn_ont(self, r):
    '''Calculate ontology values.'''
    try:
      score_prev = r[self.col_fn_ont]
    except KeyError:
      score_prev = 1
    ont   = int(r['ont_gene'], 2) & int(r['ont_host'], 2)
    score = str(bin(ont)).count('1')
    score += r['gene'] == r['host']
    return exp(score) * score_prev

  def score_keq(self, frame):
    logger.debug('[ScoreKeq] Begin Apply')
    frame['s_keq'] = self._get_column(frame, self._fn_keq)
    logger.debug('[ScoreKeq] Begin Sort')
    s_frame = frame.sort_values('s_keq', ascending=False)
    logger.debug('[ScoreKeq] Begin Reindex')
    s_frame.index = range(1, len(s_frame) + 1)
    logger.debug('[ScoreKeq] Done')
    return s_frame

  def score_deg(self, frame):
    logger.debug('[ScoreDeg] Begin')
    self.__deg_graph__ = self.as_graph(frame)
    frame['s_deg'] = self._get_column(frame, self._fn_deg)
    logger.debug('[ScoreDeg] Begin Sort')
    s_frame = frame.sort_values('s_deg', ascending=False)
    logger.debug('[ScoreDeg] Begin Reindex')
    s_frame.index = range(1, len(s_frame) + 1)
    logger.debug('[ScoreDeg] Done')
    return s_frame

  def score_ont(self, frame):
    logger.debug('[ScoreOnt] Begin')
    frame['s_ont'] = self._get_column(frame, self._fn_ont)
    logger.debug('[ScoreOnt] Begin Sort')
    s_frame = frame.sort_values('s_ont', ascending=False)
    logger.debug('[ScoreOnt] Begin Reindex')
    s_frame.index = range(1, len(s_frame) + 1)
    logger.debug('[ScoreOnt] Done')
    return s_frame

  def as_graph(self, frame):
    logger.debug('[GraphKit] Begin')
    g = nx.DiGraph()
    g.add_edges_from(frame.loc[:,('mirna', 'gene')].values)
    g.add_edges_from(frame.loc[:,('host', 'mirna')].values)
    gk = GraphKit(g)
    logger.debug('[GraphKit] End')
    return gk

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

  def _node_rank(self, frame, kind, nodes):
    score = lambda x: frame.loc[frame[kind] == x][self.col_ranks].sum()
    return list(map(score, nodes))

  def _mirna_rank(self, frame):
    return self._node_rank(frame, 'mirna', g.mirnas)

  def _gene_rank(self, frame):
    return self._node_rank(frame, 'gene', g.genes)


class Score_K_O_D(Pipeline):
  '''Score in KOD order.
  Calculate the score in following order:
    1. K equivalent (thermodynamics)
    2. Ontology
    3. Degree Score
  Thresholds applied at stage 2.
  '''
  col_fn_ont = 's_keq'
  col_fn_deg = 's_ont'
  col_ranks  = 's_deg'
  slices     = [exp(-4), exp(4)]

  @mproperty
  def stack(self):
    first_pass  = self.score_keq(self.frame.merged)
    second_pass = self.score_ont(first_pass)
    sliced      = first_pass.query('{0} < s_ont < {1}'.format(*self.slices))
    third_pass  = self.score_deg(sliced)
    return third_pass
