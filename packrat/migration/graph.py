#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import json
import logging
import networkx as nx
import pandas as pd

from miriam import psql
from packrat import catalogue

def _generate_network(target_file, host_file):
  """Grow NetworkX graph object from JSON Dumps"""
  with open(target_file, 'r') as m:
    json_targets = json.load(m)
  with open(host_file, 'r') as m:
    json_hosts = json.load(m)

  g = nx.DiGraph()

  for mir, targets in json_targets.items():
    g.add_node(mir, kind='MIR', tc=0)
    for target, trans_cnt in targets:
      g.add_node(target, kind='GEN', tc=trans_cnt)

  for mir, (host, trans_cnt) in json_hosts.items():
    g.add_node(mir, kind='MIR', tc=trans_cnt)
    g.add_node(host, kind='GEN', tc=trans_cnt)

  for mir, targets in json_targets.items():
    for target, trans_cnt in targets:
      g.add_edge(mir, target, kind='M>G')

  for mir, (host, trans_cnt) in json_hosts.items():
    g.add_edge(host, mir, kind='G>M')

  return g

def persist(version):
  """Generate Network for a specific version of JSON dump."""
  host = catalogue['network'][version]['hosts']
  targets = catalogue['network'][version]['targets']

  g = _generate_network(targets, host)
  logging.info("Network Grown")
  edge_list = nx.to_edgelist(g)

  df = pd.DataFrame(edge_list, columns=['src', 'tgt', '_'])
  del df['_']
  df.to_sql('ntwk', psql, index=False, if_exists='replace')
  logging.info("SQL Dumped: Network")

  genes = ([_[0], _[1]['tc']] for _ in g.nodes(True) if _[1]['kind'] == 'GEN')
  mirna = (_[0] for _ in g.nodes(True) if _[1]['kind'] == 'MIR')

  df_gene = pd.DataFrame(genes, columns=['symbol', 'tc'])
  df_gene = df_gene.set_index('symbol')
  df_gene.to_sql('gene', psql, if_exists='replace')
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
  df_mirna = df_mirna.set_index('symbol')
  df_mirna.to_sql('mirn', psql, if_exists='replace')
  logging.info("SQL Dumped: miRNA")

def get():
  """Return networkx object from Database"""
  network = pd.read_sql_table('ntwk', psql)
  mirna = pd.read_sql_table('mirn', psql).set_index('symbol')
  mirna['kind'] = 'MIR'

  graph = nx.from_edgelist(network.values, create_using=nx.DiGraph())
  nx.set_node_attributes(graph, 'kind', 'GEN')
  nx.set_node_attributes(graph, 'kind', mirna.loc[:,('kind')].to_dict())

  return graph
