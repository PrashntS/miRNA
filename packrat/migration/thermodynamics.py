#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
import pandas as pd

from tqdm import tqdm
from multiprocessing import Pool
from metarna.target_scan import free_energy

from miriam import psql
from miriam.network import g

def _generate_ground_work():
  """Build the Joins on Database tables to return Sequences of miRNAs and Genes
  Returns pandas dataframe having 'mirna', 'gene', 'mir_seq', 'gen_seq' cols.
  """
  seqs = pd.read_sql_table('seq', psql)
  interacts = pd.DataFrame(g.g.edges(g.mirnas), columns=['mirna', 'gene'])
  pass1 = interacts.merge(seqs, left_on='mirna', right_on='symbol')
  del interacts
  del pass1['symbol']
  pass2 = pass1.rename(columns={'sequence': 'mir_seq'})
  del pass1
  pass3 = pass2.merge(seqs, left_on='gene', right_on='symbol')
  del seqs
  del pass3['symbol']
  pass4 = pass3.rename(columns={'sequence': 'gen_seq'})
  del pass3
  return pass4

def routine():
  dg = lambda x: free_energy(x[3], x[2])

  initial = _generate_ground_work()[:10]
  initial['dg'] = initial.apply(dg, axis=1)
  return initial

def process_chunk(chunk):
  dg = lambda x: free_energy(x[3], x[2])
  chunk['dg'] = chunk.apply(dg, axis=1)
  return chunk

def step_range(lim, step, chunks):
  # [(0, 10), (10, 20), ]
  opts = [[i, i+step] for i in range(0, lim, step)]
  a, _ = opts.pop()
  opts.append([a, lim])

  return [opts[i:i+chunks] for i in range(0, len(opts), chunks)]

def coroutine():
  df = _generate_ground_work()

  passes = []
  pool = Pool(processes = 4)
  #: Process n in each pass.
  for cx in tqdm(step_range(len(df), 500, 4)):
    passes.append(pool.map(process_chunk, [df[_[0]: _[1]] for _ in cx]))

  return passes
