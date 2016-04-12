#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import hug
import falcon

from miriam.alchemy.rank import TissueCollection, Tissue
from miriam.api.directives import id_format, kind

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

@hug.get('/{kind}/{tissue_id}')
def get_rank(tissue_id: id_format, kind: kind):
  return 'test'
