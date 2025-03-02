#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import json
import logging
import networkx as nx
import pandas as pd

from pybloomfilter import BloomFilter

from packrat import catalogue, psql, db

misc_meta = db['misc_meta']
SOURCES = ['PharmGKB', 'KEGG', 'SMPDB', 'PID']


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


def _generate_functional_vectors(function_file):
  with open(function_file, 'r') as fl:
    clsfn = json.load(fl)

  kys = list(clsfn.keys())
  kys.sort()

  assoc = lambda x, c, clsfn=clsfn: str(int(x in clsfn[c]))
  funcf = lambda x, assoc=assoc, kys=kys: hex(int(''.join([assoc(x, c) for c in kys]), 2))
  return funcf, kys


def _generate_pathway_vectors(data_file):
  with open(data_file, 'r') as fl:
    pwv = json.load(fl)

  for srk in SOURCES:
    dats  = list(filter(lambda x: x[0] == srk, pwv))
    kys   = [x[1] for x in dats]
    kys.sort()
    clsfn = {x[1]: x[2] for x in dats}
    assoc = lambda x, c, clsfn=clsfn: str(int(x in clsfn[c]))
    funcf = lambda x, assoc=assoc, kys=kys: hex(int(''.join([assoc(x, c) for c in kys]), 2))
    yield funcf, kys


def persist():
  """Generate Network for a specific version of JSON dump."""
  host    = catalogue['network']['hosts']
  targets = catalogue['network']['targets']
  fncnl   = catalogue['functional_classification']['path']
  pwont   = catalogue['pathway_ontology']['path']

  g = _generate_network(targets, host)
  logging.info("Network Grown")
  edge_list = nx.to_edgelist(g)

  df = pd.DataFrame(edge_list, columns=['src', 'tgt', '_'])
  del df['_']
  df.to_sql('ntwk', psql, index=False, if_exists='replace')
  logging.info("SQL Dumped: Network")

  funcf, kys = _generate_functional_vectors(fncnl)
  ontfncts   = list(_generate_pathway_vectors(pwont))

  misc_meta.update({'namespace': 'fnclass'}, {
    'namespace': 'fnclass',
    'classes': kys,
  }, True)

  logging.info("Generating Function Vectors")

  genes = []

  for _ in g.nodes(True):
    if _[1]['kind'] == 'GEN':
      dat = [_[0], _[1]['tc'], funcf(_[0])]
      for fnont, kys in ontfncts:
        dat.append(fnont(_[0]))
      genes.append(dat)

  for i, _ in enumerate(SOURCES):
    ns = '{0}{1}'.format('ont_', _.lower())
    misc_meta.update({'namespace': ns}, {
      'namespace': ns,
      'classes': ontfncts[i][1],
    }, True)

  mirna = (_[0] for _ in g.nodes(True) if _[1]['kind'] == 'MIR')

  cols = ['symbol', 'tc', 'ont_fnc'] + list(map(lambda x: 'ont_{0}'.format(x.lower()), SOURCES))

  df_gene = pd.DataFrame(genes, columns=cols)
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
  graph = nx.from_edgelist(network.values, create_using=nx.DiGraph())

  mirna = pd.read_sql_table('mirna', psql)
  mirnas = BloomFilter(3000,  0.0001)
  for node in mirna['symbol']:
    mirnas.add(node)

  return graph, mirnas


def function_classes():
  """Return Functional Classes"""
  return misc_meta.find_one({'namespace': 'fnclass'}).get('classes')
