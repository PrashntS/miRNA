#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from metarna.target_scan import free_energy, scan as target_scan

from packrat import db
from miriam.alchemy.docs import Gene, MiRNA

class Thermodynamics(object):
  def __init__(self, bulk=False, **kwargs):
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
    self.bulk = bulk
    if bulk:
      self.gen_set = {_['gene_id']: _ for _ in db['ensembl_seq'].find()}
      self.mir_set = {_['mir_id']: _ for _ in db['mirna_seq'].find()}

    self.miranda_args.update(kwargs.get("miranda_args", {}))

  def __delta_g_single(self, gene_id, mirna_id):
    gen = Gene(gene_id).canonical
    mir = MiRNA(mirna_id).sequence
    return free_energy(gen, mir, **self.miranda_args)

  def __delta_g_bulk(self, gene_id, mirna_id):
    gen = max(
      self.gen_set[gene_id]['fasta'],
      key=lambda x: len(x['seq'])
    )['seq']
    mir = self.mir_set[mirna_id]['fasta'][0]['seq']
    return free_energy(gen, mir)

  def delta_g(self, gene_id, mirna_id):
    if self.bulk:
      return self.__delta_g_bulk(gene_id, mirna_id)
    else:
      return self.__delta_g_single(gene_id, mirna_id)

  def report(self, gene_id, mirna_id):
    gen = Gene(gene_id).canonical
    mir = MiRNA(mirna_id).sequence
    return target_scan(gen, mir, **self.miranda_args)
