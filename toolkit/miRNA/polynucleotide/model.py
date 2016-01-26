#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import request

from miRNA import db, app

class BaseDocument(db.Document):
  symbol = db.StringField(unique = True)
  FASTA  = db.StringField()

  description = db.StringField()

  meta = {
    'allow_inheritance': True,
    'strict': False,
  }

  def __unicode__(self):
    return self.symbol

class Gene(BaseDocument):
  names = db.ListField(db.StringField())

class miRNA(BaseDocument):
  mirbase_url = db.StringField()
