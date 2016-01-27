#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import request

from miRNA import db, app, zdb

graph = zdb.root.nxGraph

class Polynucleotide(db.Document):
  symbol = db.StringField(unique = True)
  FASTA  = db.StringField()

  description = db.StringField()

  meta = {
    'allow_inheritance': True,
    'strict': False,
  }

  def __unicode__(self):
    return self.symbol

class Gene(Polynucleotide):
  names = db.ListField(db.StringField())

  @property
  def _repr(self):
    desc = self.description + ' '.join(self.names)
    return {
      'id': self.symbol,
      'symbol': self.symbol,
      'description': desc,
      'degree': graph.degree(self.symbol),
      'kind': 'Gene',
    }

class miRNA(Polynucleotide):
  mirbase_url = db.StringField()

  @property
  def _repr(self):
    return {
      'id': self.symbol,
      'symbol': self.symbol,
      'description': self.description,
      'degree': graph.degree(self.symbol),
      'kind': 'miRNA',
    }
