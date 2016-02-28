#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import json
import networkx as nx
from packrat import logger

def grow_network(target_file, host_file):
  """
  Grow NetworkX graph object for persistence.
  """
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

  logger.info("Graph object generated.")

  return g
