#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
# 22 Feb 2016
import click
import csv

from minion import mincli
from miRNA.graph import g
from miRNA.alchemy.expression import ExpressionAtlas
from miRNA.stats.thermodynamics import Thermodynamics

# I have to do the following here
# - For the tissue, "pancreas", I have to generate:
# -- miRNAs that are expressed in the tissue
# -- Generate a table of the miRNAs targets and corresponding delta g.

@mincli.command("feb22")
@click.argument('output', type=click.File('w'))
def routine(output):
  """
  Tabulate the expressed miRNAs, and genes with the expression values.
  """
  atlas = ExpressionAtlas()
  atlas.tissue = 'pancreas'

  mirna_known_host = [_ for _ in g.mirnas if len(g.host(_))]
  mirna_known_host.sort(key=lambda x: len(g.target(x)), reverse=True)

  fieldnames = ['MIRNA', 'HOST', 'HOST_EXPR', 'HOST_TC', 'TARGET', 'TAR_EXPR',
    'TAR_TC', 'DELTAG',
  ]
  csvsheet = csv.writer(output, delimiter='\t')
  csvsheet.writerow(fieldnames)
  click.echo("Starting Routine")

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
      host_trns = -1.0

    filt = atlas.nbunch(targets)['available']

    for target in filt:
      row = [mirna, host_expr, host_trns, target, atlas.expr_level(target)]
      try:
        tar_trns = g.transc_count(target)
      except Exception:
        tar_trns = -1.0

      row.append(tar_trns)

      try:
        dg = Thermodynamics(target, mirna).delta_g_binding
        row.append(dg)
        csvsheet.writerow(row)
        click.echo("Done: {0},\t\t{1}".format(mirna, target))
      except Exception as e:
        click.echo("Missed: {0},\t\t{1}".format(mirna, target))
        continue

  return 0
