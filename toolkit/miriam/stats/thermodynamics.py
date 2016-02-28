#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from metarna.target_scan import free_energy, scan as target_scan

from miriam.alchemy.docs import Gene, MiRNA

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

  def delta_g(self, gene_id, mirna_id):
    gen = Gene(gene_id).canonical
    mir = MiRNA(mirna_id).sequence
    return free_energy(gen, mir, **self.miranda_args)

  def report(self, gene_id, mirna_id):
    gen = Gene(gene_id).canonical
    mir = MiRNA(mirna_id).sequence
    return target_scan(gen, mir, **self.miranda_args)
