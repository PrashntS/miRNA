#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import transaction
import networkx as nx

from miRNA import zdb, app

def graph(dat):
  """
  Migrates the Frozen Copy of Graph from JSON to Zeo DB cache.
  """
  g = nx.DiGraph()

  app.logger.info('Building the network')

  for m_key, m_dat in dat.items():
    fam = m_dat.get('family')
    mtc = m_dat.get('miRNA Transcript Count')
    g.add_node(m_key, kind = 'MIR', family = fam, tc = mtc)

    targets = m_dat.get('target_gene_tc')

    for g_id, tr_c, _ in targets:
      g.add_node(g_id, kind = 'GEN', tc = tr_c)
      g.add_edge(m_key, g_id, kind = 'M>G')

    if 'Host Gene' in m_dat:
      g_id = m_dat.get('Host Gene')
      gtc = m_dat.get('Host Gene Transcript Count', 0)
      g.add_node(g_id, kind = 'GEN', tc = gtc)
      g.add_edge(g_id, m_key, kind = 'G>M')

    app.logger.info('Added miRNA Node {0} with {1} targets.'.format(m_key, len(targets)))

  zdb.root()['nxGraph'] = nx.freeze(g)
  app.logger.info('Frozen graph object added to Zeo DB instance')

  transaction.commit()
