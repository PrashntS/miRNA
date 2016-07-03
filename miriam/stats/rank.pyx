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
from miriam.network.algorithm import Motif
from packrat.migration.graph import function_classes
from miriam.alchemy.utils import mproperty
from miriam.alchemy.rank import Tissue


cdef float R = 8.314
cdef float T = 303
cdef float RTI = -1.0 / (R * T)
cdef float e = exp(1)


class Frame(object):
  def __init__(self, tissue):
    if type(tissue) is str:
      tissue = Tissue(tissue)
    self.tissue = tissue

  @mproperty
  def ontology(self):
    data  = pd.read_sql_table('gene', psql)
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
    merge_ontology_host = merge_ontology_gene.merge(self.ontology,
      left_on='host',
      right_on='symbol')
    del merge_ontology_host['symbol']

    return merge_ontology_host

  @mproperty
  def diseases(self):
    logger.debug('[Diseases] Reading DB')
    df = (pd.read_sql_table('d_disgenenet', psql)
        .set_index('index')
        .rename(columns=dict(geneName='gene', diseaseName='disease')))
    return df.loc[df.score >= 0.5]


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

    scs = ['ont_fnc', 'ont_pharmgkb', 'ont_kegg', 'ont_smpdb', 'ont_pid']
    score = 0x0
    for ont in scs:
      rt = ont + '_x'
      lt = ont + '_y'
      ont = int(r[rt], 16) & int(r[lt], 16)
      score += str(bin(ont)).count('1')
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

  @mproperty
  def nx_graph(self):
    logger.debug('[NxGraph] Begin')
    g = nx.DiGraph()
    g.add_weighted_edges_from((self
        .stack
        .loc[:,('mirna', 'gene', self.col_ranks)]
        .values))
    logger.debug('[NxGraph] End')
    return g

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
          score += mir_scores[v]
        else:
          score += gene_scores[v]
      return formats[kind].format(**motif), score

    return {k: [motif_fmt(m, k) for m in v] for k, v in self.graph.motif.items()}

  def report(self):
    genes = self.genes
    genes.sort(key=lambda x: x[0])

    mirnas = self.mirnas
    mirnas.sort(key=lambda x: x[0])

    as_list = lambda *x: [j for i in x for j in i]
    motifs_mapped = dict(as_list(*self.motifs.values()))
    motifs = [motifs_mapped.get(_, 0.0) for _ in g.motif_hash]

    fmt_interaction = lambda x: ('{0} {1}'.format(x[0], x[1]), x[2])
    interactions = self.stack.loc[:, ('mirna', 'host', self.col_ranks)].values
    interactions_formatted = dict(map(fmt_interaction, interactions))

    interactions = [interactions_formatted.get(_, 0.0) for _ in g.interaction_hash]

    return {
      'tissue': self.frame.tissue.id,
      'genes': [x[1] for x in genes],
      'mirnas': [x[1] for x in mirnas],
      'motifs': motifs,
      'interactions': interactions,
    }

  @mproperty
  def diseases(self):
    genes_frame = pd.DataFrame(self.genes, columns=('gene', 'score'))
    groups = (self.frame
      .diseases
      .merge(genes_frame, left_on='gene', right_on='gene'))

    groups['scored'] = (groups.score_x * groups.score_y)
    scored = groups.groupby('disease')
    out = []
    for group_name in scored.groups:
      group = scored.get_group(group_name)
      score = group.scored.sum() / len(group)
      out.append([group_name, score])
    out.sort(key=lambda x: x[1], reverse=True)
    return out


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
    sliced      = second_pass.query('{0} < s_ont < {1}'.format(*self.slices))
    third_pass  = self.score_deg(sliced)
    return third_pass
