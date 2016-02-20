#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from miRNA import memcache
from mirmap import miRmap
from packrat import c_ensembl_seq, c_mirna_seq

class Thermodynamics(object):
  def __init__(self, gene_id, mirna_id, **kwargs):
    #: Get Gene Sequences
    self.gen = c_ensembl_seq.find_one({'gene_id': gene_id})
    self.mir = c_mirna_seq.find_one({'mir_id': mirna_id})
    self.__process_seq()

    miRmap_args = {
      'seq_mir': self.mir_seq,
      'seq_mrn': self.gen_seq,
      'seed_args': {
        'allowed_lengths': [6, 7],
        'allowed_gu_wobbles': {6: 0, 7: 0},
        'allowed_mismatches': {6: 0, 7: 0},
        'take_best': True
      },
    }
    miRmap_args.update(kwargs.get('miRmap_args', {}))
    self.miRmap = miRmap(**miRmap_args)

  def __preprocess_seq(self, seqs):
    return ''.join([_['seq'] for _ in seqs]).replace('T', 'U')

  def __process_seq(self):
    self.gen_seq = self.__preprocess_seq(self.gen['fasta'])
    self.mir_seq = self.__preprocess_seq(self.mir['fasta'])

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
