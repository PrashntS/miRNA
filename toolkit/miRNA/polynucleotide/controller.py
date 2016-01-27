#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask.ext.mongorest import operators as ops
from flask.ext.mongorest.resources import Resource

from miRNA.polynucleotide.model import Gene, miRNA

class SymbolicResource(Resource):
  max_limit = 20
  def get_object(self, pk, qfilter=None):
    qs = self.get_queryset()

    if qfilter:
      qs = qfilter(qs)

    return qs.get(symbol = pk)

class GeneResource(SymbolicResource):
  document = Gene
  fields = ['id', 'symbol', 'description', 'names',]

class miRNAResource(SymbolicResource):
  document = miRNA
  fields = ['id', 'mirbase_url', 'symbol']
