#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
# 27 Feb 2016
import click
import csv
import math
import pickle
import pandas as pd

R = 8.314
T = 303

def routine(filename):
  """
  Evaluate the tables.
  """
  with open(filename, 'rb') as pickled:
    df = pickle.load(pickled)
  #: Function to obtain the ranks
  mic_reg = lambda x: math.exp((-1 * x[7]) / (R * T)) * x[3] * x[2]* x [6] * x[5]
  reg_pot = lambda x: math.exp((-1 * x[7]) / (R * T)) * x[3] * x[2]* x [6] / x[5] if x[5] else None

  mir_expr = lambda x: x[2] if x[2] >= 0 else 0
  tar_expr = lambda x: x[5] if x[5] >= 0 else 0
  df['HOST_EXPR'] = df.apply(mir_expr, axis=1)
  df['TAR_EXPR'] = df.apply(tar_expr, axis=1)

  rank_func = lambda x: math.exp((-1 * x[7]) / (R * T)) * (x[2] / x[5]) * (x[9] / x[8]) if (x[5] > 0 and x[2] > 0) else None

  #: Add a new column by applying function on each row
  df['RANK'] = df.apply(rank_func, axis=1)

  log_r = lambda x: math.log10(x[11])
  df['RANK_LG'] = df.apply(log_r, axis=1)

  df = df.sort_values("RANK", ascending=False)
  df.index=range(1, len(df) + 1)
  return df
