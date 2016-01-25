#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import request

from miRNA import db, app

class Gene(db.Document):
  symbol = db.StringField(unique = True)
  FASTA  = db.StringField()
  names  = db.ListField(db.StringField())

  description       = db.StringField()

  meta = {
    'allow_inheritance': True,
    'strict': False,
  }

  def __unicode__(self):
    return self.symbol

class miRNA(db.Document):
  symbol  = db.StringField(unique = True)
  FASTA   = db.StringField()

  mirbase_url = db.StringField()

  meta = {'allow_inheritance': True, 'strict': False}

  def __unicode__(self):
    return self.symbol


