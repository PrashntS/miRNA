#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import math
import pandas as pd

from packrat import logger
from miriam.graph import g
from miriam.alchemy.expression import ExpressionAtlas
from miriam.stats.thermodynamics import Thermodynamics

R = 8.314
T = 303

def ranking_routine(output, tissue='pancreas', namespace='EMTAB2919'):
  """
  Tabulate the expressed miRNAs, and genes with the expression values.
  """
  logger.info("Obtaining Bulk Data.")

  thermo = Thermodynamics(bulk=True)
  atlas = ExpressionAtlas(namespace, bulk=True)
  atlas.tissue = tissue

  logger.info("Generating MiRNA List.")

  mirna_known_host = [_ for _ in g.mirnas if len(g.host(_))]
  mirna_known_host.sort(key=lambda x: len(g.target(x)), reverse=True)

  rows = []

  logger.info("Generating Interaction List.")

  for mirna in mirna_known_host:
    targets = g.target(mirna)
    host = g.host(mirna)[0]
    for target in targets:
      rows.append([mirna, host, target])

  logger.info("Preparing DataFrame of Interactions.")

  df = pd.DataFrame(rows, columns=['MIRNA', 'HOST', 'TARGET'])

  def host_expr(row):
    try:
      return atlas.expr_level(row[1])
    except ValueError:
      return 0.0

  def targ_expr(row):
    try:
      return atlas.expr_level(row[2])
    except ValueError:
      return 0.0

  def delta_g(row):
    try:
      return thermo.delta_g(row[2], row[1])
    except Exception:
      return 1

  logger.info("Obtaining Host Expressions.")
  df['HOST_EXPR'] = df.apply(host_expr, axis=1)

  logger.info("Obtaining Target Expressions.")
  df['TAR_EXPR'] = df.apply(targ_expr, axis=1)

  logger.info("Obtaining Delta G Values.")
  df['DELTAG'] = df.apply(delta_g, axis=1)

  logger.info("Obtaining MiRNA Degrees.")
  df['DEGM'] = df.apply(lambda x: len(g.target(x[0])), axis=1)

  logger.info("Obtaining Target Degrees.")
  df['DEGT'] = df.apply(lambda x: len(g.target(x[2])), axis=1)

  def rank(row):
    if (row[4] > 0 and row[3] > 0):
      keq = math.exp((-1 * row[5]) / (R * T))
      ex_ratio = (row[3] / row[4])
      deg_ratio = (row[6] / row[7])
      return keq * ex_ratio * deg_ratio
    else:
      return None

  logger.info("Obtaining Ranks.")
  df['RANK'] = df.apply(rank, axis=1)

  log_r = lambda x: math.log10(x[8])

  logger.info("Obtaining Logarithmic Ranks.")
  df['RANK_LG'] = df.apply(log_r, axis=1)

  logger.info("Sorting Ranks.")
  df = df.sort_values("RANK", ascending=False)

  logger.info("Reindexing.")
  df.index=range(1, len(df) + 1)

  logger.info("Finishing Up.")
  df.to_pickle("{0}_{1}_{2}.pkl".format(output, namespace, tissue))

  logger.info("Ranking Completed for {0}-{1}".format(namespace, tissue))
