#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import hug
import falcon

from miriam.alchemy.rank import TissueCollection, Tissue
from miriam.api.directives import id_format, kind
from miriam.stats.rank import Ranking

@hug.get('/tissues')
def get_tissues():
  tissues = TissueCollection()
  return tissues.repr

@hug.get('/tissues/{tissue_id}')
def get_tissues_via_id(tissue_id: id_format):
  try:
    tissue = Tissue(tissue_id)
    return tissue.repr
  except KeyError:
    raise falcon.HTTPNotFound

@hug.get('/{tissue_id}')
def get_rank_summary(tissue_id: id_format):
  try:
    tissue = Tissue(tissue_id)
    r_o = Ranking(tissue)
    return r_o.report
  except KeyError:
    raise falcon.HTTPNotFound
