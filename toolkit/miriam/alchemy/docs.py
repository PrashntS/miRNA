#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from packrat import db
from miriam.graph import g

class Gene(object):
  def __init__(self, gene_id):
    coll = db['ncbi_gene_docs']
    self.gid = gene_id
    self.doc = coll.find_one({'gene_id': gene_id})

    if self.doc is None:
      raise KeyError("{0} is not in the collection.".format(gene_id))

  @property
  def synonyms(self):
    out = self.doc['synonyms']
    if type(out) is str:
      out = [out]
    return out

  @property
  def repr(self):
    return {
      'symbol': self.gid,
      'name': self.doc.get('name'),
      'synonyms': self.synonyms,
      'summary': self.doc.get('summary'),
      'protein_ref': self.doc.get('protein_ref'),
      'functions': self.doc.get('functions'),
      'processes': self.doc.get('processes'),
      'len_targeted_by': len(self.targeted_by),
      'len_host_of': len(self.host_of),
      'kind': 'Gene',
    }

  @property
  def sequences(self):
    seq = db['ensembl_seq'].find_one({'gene_id': self.gid})
    return seq['fasta']

  @property
  def canonical(self):
    return max(self.sequences, key=lambda x: len(x['seq']))['seq']

  @property
  def host_of(self):
    return g.host(self.gid)

  @property
  def targeted_by(self):
    return g.target(self.gid)

class MiRNA(object):
  def __init__(self, mir_id):
    coll = db['mirna_seq']
    self.mid = mir_id

  @property
  def sequence(self):
    seqd = db['mirna_seq'].find_one({'mir_id': self.mid})
    return seqd['fasta'][0]['seq']

  @property
  def repr(self):
    return {
      'symbol': self.mid,
      'len_targets': len(self.targets),
      'host': self.host_gene,
      'kind': 'MiRNA',
    }

  @property
  def targets(self):
    return g.target(self.mid)

  @property
  def host_gene(self):
    return g.host(self.mid)
