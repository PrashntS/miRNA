#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import request

from miRNA import db, app

class miRNAGeneTargetedByComplex(db.EmbeddedDocument):
  miRNA     = db.ReferenceField('miRNA')
  affinity  = db.FloatField()

  meta = {'allow_inheritance': True, 'strict': False}

class Gene(db.Document):
  symbol = db.StringField(unique = True)
  FASTA  = db.StringField()
  names  = db.ListField(db.StringField())

  description       = db.StringField()
  transcript_count  = db.IntField()

  host_of = db.ReferenceField('miRNA')
  targeted_by = db.ListField(db.EmbeddedDocumentField(miRNAGeneTargetedByComplex))

  searchable = db.StringField()

  meta = {
    'allow_inheritance': True,
    'strict': False,
  }

  def __unicode__(self):
    return self.symbol

  @property
  def tr(self):
      return '{0}-{1}'.format(self.symbol, self.host_of.symbol)

class miRNAGeneTargetComplex(db.EmbeddedDocument):
  gene      = db.ReferenceField(Gene)
  affinity  = db.FloatField()

  meta = {'allow_inheritance': True, 'strict': False}

class miRNA(db.Document):
  symbol  = db.StringField(unique = True)
  FASTA   = db.StringField()
  host    = db.ReferenceField(Gene)
  targets = db.ListField(db.EmbeddedDocumentField(miRNAGeneTargetComplex))

  mirbase_url = db.StringField()
  transcript_count = db.IntField()

  searchable = db.StringField()

  meta = {'allow_inheritance': True, 'strict': False}

  def __unicode__(self):
    return self.symbol

  @property
  def tr(self):
      return '{0}'.format(self.symbol)

