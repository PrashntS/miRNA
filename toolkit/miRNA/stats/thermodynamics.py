#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from miRNA import memcache
from mirmap import miRmap
from miRNA.alchemy.docs import Gene, MiRNA

class Thermodynamics(object):
  def __init__(self, gene_id, mirna_id, **kwargs):
    #: Get Gene Sequences
    self.gen = Gene(gene_id)
    self.mir = MiRNA(mirna_id)
    self.__process_seq()
    self.__mirmap_init(**kwargs)

  def __mirmap_init(self, **kwargs):
    miRmap_args = {
      'seq_mir': self.mir_seq,
      'seq_mrn': self.gen_seq,
      'seed_args': {
        'allowed_lengths': [6, 7, 8],
        'allowed_gu_wobbles': {6: 0, 7: 0, 8: 0},
        'allowed_mismatches': {6: 0, 7: 0, 8: 0},
        'take_best': True
      },
      'thermo_args': {
        'temperature': 36.0
      }
    }
    miRmap_args.update(kwargs.get('miRmap_args', {}))
    self.miRmap = miRmap(**miRmap_args)

  def __process_seq(self):
    self.gen_seq = self.gen.canonical.replace('T', 'U')
    self.mir_seq = self.mir.sequence

  @property
  def delta_g_binding(self):
      thermo_vals = self.miRmap.thermodynamic_features
      return thermo_vals['dg_binding']

  @property
  def report(self):
    return self.miRmap.report

@memcache.cached()
def get_delta_g_binding(gene_id, mirna_id):
  try:
    obj = Thermodynamics(gene_id, mirna_id)
    return obj.delta_g_binding
  except ValueError:
    return 10
