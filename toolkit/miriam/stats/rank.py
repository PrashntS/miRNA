#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import math
import pandas as pd
import networkx as nx
import functools

from multiprocessing import Pool

from miriam import psql

R = 8.314
T = 303

class Ranking(object):
  def __init__(self):
    # Thresholds
    self.th_ps1 = 1
    self.th_ps2 = 1
    self.__proc = 3

    self.tissue = 'aorta'
    self.namespace = 'e_emtab2919'
    self.__preinit()
    self.__setup_ground()
    # self.__setup_deg_rank()

  def __preinit(self):
    self.ntwkdg = pd.read_sql_table('ntwkdg', psql)
    self.mirna  = pd.read_sql_table('mirn', psql)

    self.exp_dat = pd.read_sql_query(
      'select gene_name, {0} from {1}'.format(self.tissue, self.namespace),
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

  def _f_r1(self, x):
    if x[3] == 0:
      return None
    else:
      return math.exp(-x[2] / (R * T)) * (x[5] / x[3])

  def __setup_ground(self):
    """Adds First Ranking to the DataFrame.
    [Caveates] Added column: `r1`, index: 6
    """
    gd = self.__do_merge()

    #: Calculate keq.

    gd['r1'] = self.__coroutine_apply('_f_r1', gd)#  gd.apply(f_r1_p2, axis=1)

    gd_p1 = gd.sort_values('r1', ascending=False)
    gd_p1.index = range(1, len(gd_p1) + 1)
    self.gd_p1 = gd_p1

  def __setup_deg_rank(self):
    p2 = self.gd_p1.query('r1 > {0}'.format(math.exp(self.th_ps1)))
    g_p2 = nx.from_edgelist(p2.loc[:,('mirna', 'gene')].values,
        create_using=nx.DiGraph())
    f_r2 = lambda x: x[6] * g_p2.degree(x[1]) / g_p2.degree(x[0])

    p2['r2'] = self.__coroutine_apply(f_r2, p2)# p2.apply(f_r2, axis=1)

    gd_p2 = p2.sort_values('r2', ascending=False)
    gd_p2.index = range(1, len(gd_p2) + 1)
    self.gd_p2 = gd_p2

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


    for cx in self.__srange(len(frame), 10000, self.__proc):
      chunks = [[func, frame[_[0]:_[1]]] for _ in cx]
      res = pool.map(self._process_chunk, chunks)
      frame = pd.concat(list(res))
      passes.append(frame)

    return pd.concat(passes)
