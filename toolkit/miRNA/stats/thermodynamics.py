#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import json

from miRNA import memcache
from libpymiranda import find_targets as miranda_targets
from miRNA.alchemy.docs import Gene, MiRNA

class Thermodynamics(object):
  def __init__(self, gene_id, mirna_id, **kwargs):
    #: Get Gene Sequences
    self.gen = Gene(gene_id)
    self.mir = MiRNA(mirna_id)
    self.__process_seq()
    miranda_args = {
      'gene_seq': self.gen_seq,
      'mirna_seq': self.mir_seq,
      'scale': 4.0,
      'strict': 0,
      'gap_open': -9.0,
      'gap_extend': -4.0,
      'score_threshold': 10.0,
      'energy_threshold': 1.0,
      'length_5p_for_weighting': 8,
      'temperature': 30,
    }
    miranda_args.update(kwargs.get("miranda_args", {}))
    self.result = json.loads(miranda_targets(**miranda_args))

  def __process_seq(self):
    self.gen_seq = self.gen.canonical
    self.mir_seq = self.mir.sequence[::-1]

  @property
  def delta_g_binding(self):
    try:
      return self.result['digest']['max_energy']
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
