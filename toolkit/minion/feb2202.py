#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
# 22 Feb 2016
import click
import csv
import math
import pandas as pd

from minion import mincli
from miriam.graph import g
from miriam.alchemy.expression import ExpressionAtlas
from miriam.stats.thermodynamics import Thermodynamics

# I have to do the following here
# - For the tissue, "pancreas", I have to generate:
# -- miRNAs that are expressed in the tissue
# -- Generate a table of the miRNAs targets and corresponding delta g.

R = 8.314
T = 303

@mincli.command("feb22")
@click.argument('output')
@click.option('--tissue', default='pancreas')
@click.option('--namespace', default='EMTAB2919')
def routine(output, tissue, namespace):
  """
  Tabulate the expressed miRNAs, and genes with the expression values.
  """
  atlas = ExpressionAtlas(namespace, bulk=True)
  atlas.tissue = tissue

  mirna_known_host = [_ for _ in g.mirnas if len(g.host(_))]
  mirna_known_host.sort(key=lambda x: len(g.target(x)), reverse=True)

  fieldnames = ['MIRNA', 'HOST', 'HOST_EXPR', 'HOST_TC', 'TARGET', 'TAR_EXPR',
    'TAR_TC', 'DELTAG', 'DEGM', 'DEGT', 'DEGHOS',
  ]
  rows = []
  click.echo("Starting Routine")

  thermo = Thermodynamics(bulk=True)

  max_m = len(mirna_known_host)
  curr_m = 0

  for mirna in mirna_known_host:
    targets = g.target(mirna)
    host = g.host(mirna)[0]
    try:
      host_expr = atlas.expr_level(host)
    except ValueError:
      host_expr = 0.0

    try:
      host_trns = g.transc_count(host)
    except Exception:
      host_trns = 1.0

    curr_m += 1
    max_t = len(targets)
    curr_t = 0

    for target in targets:
      row = [mirna, host, host_expr, host_trns, target]
      curr_t += 1

      try:
        row.append(atlas.expr_level(target))
      except ValueError:
        row.append(0.0)

      try:
        tar_trns = g.transc_count(target)
      except ValueError:
        tar_trns = 1.0

      row.append(tar_trns)

      try:
        dg = thermo.delta_g(target, mirna)
      except Exception as e:
        dg = 1
      row.append(dg)
      row.append(max_t)
      row.append(len(g.target(target)))
      row.append(len(g.host(target)))
      rows.append(row)

      if curr_t % (int(max_t/10) + 1) is 0:
        click.echo("Done: M({0}/{1}),\t\t\t G({2}/{3})".format(
            curr_m, max_m, curr_t, max_t))

  df = pd.DataFrame(rows, columns=fieldnames)

  rank_func = lambda x: math.exp((-1 * x[7]) / (R * T)) * (x[2] / x[5]) * (x[9] / x[8]) if (x[5] > 0 and x[2] > 0) else None

  df['RANK'] = df.apply(rank_func, axis=1)

  log_r = lambda x: math.log10(x[11])
  df['RANK_LG'] = df.apply(log_r, axis=1)

  df = df.sort_values("RANK", ascending=False)
  df.index=range(1, len(df) + 1)

  df.to_pickle("{0}_{1}_{2}.pkl".format(output, namespace, tissue))

