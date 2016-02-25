#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import json

from miRNA import memcache
from pymiranda import find_targets as miranda_targets
from miRNA.alchemy.docs import Gene, MiRNA

class Thermodynamics(object):
  def __init__(self, **kwargs):
    self.miranda_args = {
      'scale': 4.0,
      'strict': 0,
      'gap_open': -9.0,
      'gap_extend': -4.0,
      'score_threshold': 50.0,
      'energy_threshold': 1.0,
      'length_5p_for_weighting': 8,
      'temperature': 30,
      'alignment_len_threshold': 8,
    }
    self.miranda_args.update(kwargs.get("miranda_args", {}))

  def __obtain_args(self, gene_id, mirna_id):
    gen = Gene(gene_id)
    mir = MiRNA(mirna_id)
    self.miranda_args['gene_seq'] = gen.canonical
    self.miranda_args['mirna_seq'] = mir.sequence[::-1]

  def delta_g(self, gene_id, mirna_id):
    try:
      gen = Gene(gene_id).canonical
      mir = MiRNA(mirna_id).sequence[::-1]
      result = json.loads(miranda_targets(gen, mir, **self.miranda_args))
      return result['digest']['max_energy']
    except KeyError:
      raise ValueError("No targets found with given parameters.")

  @property
  def report(self):
    return self.result

@memcache.cached()
def get_delta_g_binding(gene_id, mirna_id):
  try:
    obj = Thermodynamics(gene_id, mirna_id)
    return obj.delta_g_binding
  except ValueError:
    return 10
