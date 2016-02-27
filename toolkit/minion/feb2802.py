#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
# 28 Feb 2016

from miRNA.graph.triads import Motif
from miRNA.graph import g

from minion.feb2702 import routine as feb2702_routine

def routine(filename="feb25v4.pkl"):
  df = feb2702_routine(filename)
  m = Motif(g.g)
  return df, m
