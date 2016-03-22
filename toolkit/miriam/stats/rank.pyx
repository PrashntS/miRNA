#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import pandas as pd
import networkx as nx
import functools
import itertools

from multiprocessing import Pool
from pydash import py_
from math import exp
from cpython cimport array
import array

from miriam import psql, db

cdef float R = 8.314
cdef float T = 303
cdef float RTI = -1.0 / (R * T)
cdef float e = exp(1)

class Ranking(object):
  def __init__(self, tissue, table, **kwa):
    # Thresholds
    self.th_ps2 = kwa.get('th_ps2', 1)
    self.th_ps3 = kwa.get('th_ps3', 1)
    self.__proc = kwa.get('__proc', 1)

    self.tissue = tissue
    self.table = table
    self.degcache = {}
    self.__preinit()
    self.__setup_ground()

  def __preinit(self):
    self.ntwkdg = pd.read_sql_table('ntwkdg', psql)
    self.mirna  = pd.read_sql_table('mirn', psql)

    self.exp_dat = pd.read_sql_query(
      'select gene_name, {0} from {1}'.format(self.tissue, self.table),
      psql
    )

  def __do_merge(self):
    """Return Merged Data Segments

    [Caveates] Returned Columns:
      ['mirna', 'gene', 'dg', 'exp_tar', 'host', 'exp_mir']
        0        1       2     3          4       5
    """
    #: Join Target Gene Expressions
    p1 = self.ntwkdg.merge(self.exp_dat, left_on='gene', right_on='gene_name')
    del p1['gene_name']
    p1 = p1.rename(columns={self.tissue: 'exp_tar'})

    #: Join MiRNA's host genes
    p2 = p1.merge(self.mirna, left_on='mirna', right_on='symbol')
    del p2['symbol']

    p3 = p2.merge(self.exp_dat, left_on='host', right_on='gene_name')
    del p3['gene_name']
    p3 = p3.rename(columns={self.tissue: 'exp_mir'})

    del p1
    del p2
    return p3

  def _f_r1(self, row):
    cdef float dg = row[2]
    cdef float eg = row[3]
    cdef float em = row[5]
    try:
      return (e ** (RTI * dg)) * (em / eg)
    except ZeroDivisionError:
      return None

  def __degree(self, x):
    try:
      return self.degcache[x]
    except KeyError:
      deg = self.g_p2.degree(x)
      self.degcache[x] = deg
      return deg

  def _f_r2(self, row):
    cdef int dm = self.__degree(row[0])
    cdef int dg = self.__degree(row[1])
    cdef float r1 = row[6]

    return r1 * dg / dm

  def __setup_ground(self):
    """Adds First Ranking to the DataFrame.
    [Caveates] Added column: `r1`, index: 6
    """
    gd = self.__do_merge()

    #: Calculate keq.

    gd['r1'] = self.__coroutine_apply('_f_r1', gd)#  gd.apply(f_r1_p2, axis=1)
    # gd['r1'] = gd.apply(self._f_r1, axis=1)

    gd_p1 = gd.sort_values('r1', ascending=False)
    gd_p1.index = range(1, len(gd_p1) + 1)
    self.gd_p1 = gd_p1

  def __get_deg_rank(self):
    pd.options.mode.chained_assignment = None
    self.gd_p2 = self.gd_p1.query('r1 > {0}'.format(exp(self.th_ps2)))
    self.g_p2 = nx.from_edgelist(self.gd_p2.loc[:,('mirna', 'gene')].values,
        create_using=nx.DiGraph())

    self.gd_p2['r2'] = self.__coroutine_apply('_f_r2', self.gd_p2)

    gd_p3 = self.gd_p2.sort_values('r2', ascending=False)
    gd_p3.index = range(1, len(gd_p3) + 1)
    if self.th_ps3 > 0:
      gd_p3 = gd_p3.query('r2 > {0}'.format(exp(self.th_ps3)))
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

  def patch_ranks(self, threshold_ground=1, threshold_degree=1):
    self.th_ps2 = threshold_ground
    self.th_ps3 = threshold_degree
    self.__ranks = self.__get_deg_rank()

  @property
  def ranks(self):
    try:
      return self.__ranks
    except AttributeError:
      self.patch_ranks()
      return self.__ranks

  @ranks.setter
  def ranks(self, val):
    self.__ranks = val

  @property
  def report(self):
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

  def graphify(self, slice=100):
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
    if type(slice) is int:
      x, y = 0, slice
    elif type(slice) in [list, tuple]:
      x, y = slice
    else:
      raise ValueError("`slice` is invalid")

    rankbunch = self.ranks[x:y]

    g = nx.DiGraph()
    g.add_weighted_edges_from(rankbunch.loc[:,('mirna', 'gene', 'r2')].values)
    g.add_weighted_edges_from(rankbunch.loc[:,('host', 'mirna', 'exp_mir')].values)

    for i, j in [['MIR', 'mirna'], ['GEN', 'gene'], ['GEN', 'host']]:
      nx.set_node_attributes(g, 'kind', {v: i for v in rankbunch[j].values})

    return g

def get_ranks(tissue, namespace, **kwa):
  doc = db['expre_meta'].find_one({'namespace': namespace})
  if doc is not None and tissue in doc['tissues']:
    runner = Ranking(tissue, doc['db'], **kwa)
    return runner
  else:
    raise KeyError("Given tissue and namespace combination is invalid.")

