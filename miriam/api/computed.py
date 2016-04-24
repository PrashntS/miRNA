#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import hug
import falcon

from packrat import catalogue
from packrat.alchemy.utils import get_json_dict


@hug.get('/functional')
def get_computed_function():
  funcs = get_json_dict(catalogue['functional_ranks_computed']['path'])
  # Reshape funcs to streams
  to_return = []
  proc_streams = zip(*funcs.values())

  for stream in proc_streams:
    label, vals = zip(*stream)
    to_return.append({
      'key': label[0],
      'values': zip(funcs.keys(), vals, range(len(vals)))
    })

  return to_return

@hug.get('/ranksample')
def get_computed_rank():
  return get_json_dict(catalogue['ranks_sample_computed']['path'])
