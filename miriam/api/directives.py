#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import falcon

def id_format(param, **kwa):
  """Hyphen separated Namespace Symbol id."""
  try:
    ns, ti = param.split('-')
    if ns and ti:
      return param
    else:
      raise ValueError
  except ValueError:
    raise ValueError('Supplied id is invalid.')

def kind(param):
  """Node Kind (gene, or mirna)"""
  kinds = {
    'genes': 'gene',
    'mirnas': 'mirna',
  }
  if param not in kinds:
    raise ValueError('Supplied `kind` is invalid.')

  return kinds[param]
