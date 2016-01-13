#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import request
from miRNA import db, app

class Gene(db.Document):
  symbol = db.StringField()
  FASTA  = db.StringField()

  meta = {'allow_inheritance': True, 'strict': False}

  def __unicode__(self):
    return self.symbol

class miRNA(db.Document):
  symbol = db.StringField()
  FASTA  = db.StringField()

  meta = {'allow_inheritance': True, 'strict': False}

  def __unicode__(self):
    return self.symbol

class miRNAComplex(db.Document):
  gene      = db.ReferenceField(Gene)
  mirna     = db.ReferenceField(miRNA)
  affinity  = db.FloatField()

  meta = {'allow_inheritance': True, 'strict': False}

  def __unicode__(self):
    return "{0}-{1}".format(self.gene.symbol, self.mirna.symbol)
