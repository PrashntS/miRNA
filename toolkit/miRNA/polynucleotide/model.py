#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import request

from miRNA import db, app

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

  @property
  def _repr(self):
    return {
      'symbol': self.symbol,
      'description': self.description,
    }

class Gene(Polynucleotide):
  names = db.ListField(db.StringField())

  @property
  def _repr(self):
    desc = self.description + ' '.join(self.names)
    return {
      'symbol': self.symbol,
      'description': desc,
    }

class miRNA(Polynucleotide):
  mirbase_url = db.StringField()
