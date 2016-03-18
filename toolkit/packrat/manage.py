#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
"""Manager Routines For Database Prep

IMPORTANT: Only Programatic Access is provided.
"""
import logging
import networkx as nx
import pandas as pd

from miriam import psql
from packrat import catalogue
from packrat.migration.graph import grow_network

def network(version):
  """Generate Network for a specific version of JSON dump."""
  host = catalogue['network'][version]['hosts']
  targets = catalogue['network'][version]['targets']

  g = grow_network(targets, host)
  logging.info("Network Grown")
  edge_list = nx.to_edgelist(g)

  df = pd.DataFrame(edge_list, columns=['src', 'tgt', '_'])
  del df['_']
  df.to_sql('ntwk', psql, index=False, if_exists='replace')
  logging.info("SQL Dumped: Network")

  genes = ([_[0], _[1]['tc']] for _ in g.nodes(True) if _[1]['kind'] == 'GEN')
  mirna = (_[0] for _ in g.nodes(True) if _[1]['kind'] == 'MIR')

  df_gene = pd.DataFrame(genes, columns=['symbol', 'tc'])
  df_gene.to_sql('gene', psql, index=False, if_exists='replace')
  logging.info("SQL Dumped: Genes")

  host_links = [(_[0], _[1]) for _ in g.edges(data=True) if _[2]['kind'] == 'G>M']

  resolve_host = lambda x: [_[0] for _ in host_links if _[1] == x]

  def get_flat_host(row):
    candidates = resolve_host(row[0])
    try:
      return candidates[0]
    except IndexError:
      return None

  df_mirna = pd.DataFrame(mirna, columns=['symbol'])
  df_mirna['host'] = df_mirna.apply(get_flat_host, axis=1)
  df_mirna.to_sql('mirn', psql, index=False, if_exists='replace')
  logging.info("SQL Dumped: miRNA")

