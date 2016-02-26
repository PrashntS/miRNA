#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
# 22 Feb 2016
import click
import csv
import math
import pandas as pd

from minion import mincli
from miRNA.graph import g
from miRNA.alchemy.expression import ExpressionAtlas
from miRNA.stats.thermodynamics import Thermodynamics

# I have to do the following here
# - For the tissue, "pancreas", I have to generate:
# -- miRNAs that are expressed in the tissue
# -- Generate a table of the miRNAs targets and corresponding delta g.

R = 8.314
T = 303

@mincli.command("feb22")
@click.argument('output')
@click.option('--tissue', default='pancreas')
def routine(output, tissue):
  """
  Tabulate the expressed miRNAs, and genes with the expression values.
  """
  atlas = ExpressionAtlas()
  atlas.tissue = tissue

  mirna_known_host = [_ for _ in g.mirnas if len(g.host(_))]
  mirna_known_host.sort(key=lambda x: len(g.target(x)), reverse=True)

  fieldnames = ['MIRNA', 'HOST', 'HOST_EXPR', 'HOST_TC', 'TARGET', 'TAR_EXPR',
    'TAR_TC', 'DELTAG', 'DEGM', 'DEGT', 'DEGHOS'
  ]
  rows = []
  click.echo("Starting Routine")

  thermo = Thermodynamics()

  max_m = len(mirna_known_host)
  curr_m = 0

  for mirna in mirna_known_host:
    targets = g.target(mirna)
    host = g.host(mirna)[0]
    try:
      host_expr = atlas.expr_level(host)
    except ValueError:
      host_expr = -1.0

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
        row.append(-1.0)

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

  dat = pd.DataFrame(rows, columns=fieldnames)
  dat.to_pickle("{0}_{1}.pkl".format(output, tissue))
  dat.to_csv("{0}_{1}.csv".format(output, tissue))

  return 0
