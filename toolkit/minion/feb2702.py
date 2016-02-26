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

  #: Add a new column by applying function on each row
  df['MIC_REG'] = df.apply(mic_reg, axis=1)
  df['REG_POT'] = df.apply(reg_pot, axis=1)

  df = df.sort_values("MIC_REG", ascending=False)
  df = df.sort_values("REG_POT", ascending=False)
  df.index=range(1, len(df) + 1)

  print(df[0:10])
  return df
