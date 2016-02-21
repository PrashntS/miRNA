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
    self.__mirmap_init(**kwargs)

  def __preprocess_seq(self, seqs):
    return ''.join([_['seq'] for _ in seqs]).replace('T', 'U')

  def __mirmap_init(self, **kwargs):
    miRmap_args = {
      'seq_mir': self.mir_seq,
      'seq_mrn': self.gen_seq,
      'seed_args': {
        'allowed_lengths': [6, 7],
        'allowed_gu_wobbles': {6: 0, 7: 0},
        'allowed_mismatches': {6: 0, 7: 0},
        'take_best': True
      },
      'thermo_args': {
        'temperature': 25.0
      }
    }
    miRmap_args.update(kwargs.get('miRmap_args', {}))
    self.miRmap = miRmap(**miRmap_args)

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

class ThermodynamicsTranscript(object):
  def __init__(self, gene_id, mirna_id, **kwargs):
    #: Get Gene Sequences
    self.gen = c_ensembl_seq.find_one({'gene_id': gene_id})
    self.mir = c_mirna_seq.find_one({'mir_id': mirna_id})
    self.__process_seq()
    self.__mirmap_init(**kwargs)

  def __preprocess_seq(self, seqs):
    return ''.join([_['seq'] for _ in seqs]).replace('T', 'U')

  def __preprocess_trans_seq(self, seqs):
    return {_['id']: _['seq'].replace('T', 'U') for _ in seqs}

  def __process_seq(self):
    self.mir_seq = self.__preprocess_seq(self.mir['fasta'])
    self.gen_seq = self.__preprocess_trans_seq(self.gen['fasta'])

  def __mirmap_init(self, **kwargs):
    miRmap_args = lambda x: {
      'seq_mir': self.mir_seq,
      'seq_mrn': x,
      'seed_args': {
        'allowed_lengths': [6, 7],
        'allowed_gu_wobbles': {6: 0, 7: 0},
        'allowed_mismatches': {6: 0, 7: 0},
        'take_best': True
      },
      'thermo_args': {
        'temperature': 25.0
      }
    }
    self.miRmaps = {}
    for transcid, transeq in self.gen_seq.items():
      miRmap_arg = miRmap_args(transeq)
      miRmap_arg.update(kwargs.get('miRmap_args', {}))
      self.miRmaps[transcid] = miRmap(**miRmap_arg)

  @property
  def delta_g_binding(self):
    out = {}
    for transcid, mirmap in self.miRmaps.items():
      try:
        out[transcid] = mirmap.thermodynamic_features['dg_binding']
      except ValueError:
        out[transcid] = None
    return out

@memcache.cached()
def get_delta_g_binding(gene_id, mirna_id):
  try:
    obj = Thermodynamics(gene_id, mirna_id)
    return obj.delta_g_binding
  except ValueError:
    return 10
