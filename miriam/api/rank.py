#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import hug
import falcon

from miriam.alchemy.rank import TissueCollection, Tissue
from miriam.api.directives import id_format, kind
from miriam.stats.rank import Ranking

from packrat import catalogue
from packrat.alchemy.utils import get_json_dict

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
def get_rank_summary(tissue_id: id_format,
      threshold_pass_two: hug.types.number=3,
      threshold_pass_three: hug.types.number=3
  ):
  try:
    tissue = Tissue(tissue_id)
    r_o = Ranking(tissue,
        th_ps2=threshold_pass_two,
        th_ps3=threshold_pass_three)
    return r_o.report
  except KeyError:
    raise falcon.HTTPNotFound

@hug.get('/{tissue_id}/{kind}')
def get_rank_summary(tissue_id: id_format,
      kind: kind
  ):
  try:
    tissue = Tissue(tissue_id)
    r_o = Ranking(tissue)
    return r_o.ranks[kind]
  except KeyError:
    raise falcon.HTTPNotFound


@hug.get('/computedfunctions')
def get_computed_function():
  return get_json_dict(catalogue['functional_ranks_computed']['path'])
