#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
# 21 Feb 2016

from miRNA.graph import g
from miRNA.alchemy.expression import ExpressionAtlas

def routine(tissue, namespace=None):
  atlas = ExpressionAtlas(namespace)
  atlas.tissue = tissue
  filt = atlas.nbunch(g.genes)
  genes = filt['available']
  expres = [(k, atlas.expr_level(k)) for k in genes]
  expres.sort(key=lambda x: x[1])
  return expres

