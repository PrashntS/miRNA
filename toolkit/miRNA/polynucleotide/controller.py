#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask.ext.mongorest import operators as ops
from flask.ext.mongorest.resources import Resource

from miRNA.polynucleotide.model import Gene, miRNA, miRNAGeneTargetComplex

class SymbolicResource(Resource):
  # rename_fields = {
  #   'id': 'symbol',
  # }

  def get_object(self, pk, qfilter=None):
    qs = self.get_queryset()

    print(qs, pk, qfilter)
    if qfilter:
      qs = qfilter(qs)

    return qs.get(symbol = pk)

class GeneResource(SymbolicResource):
  document = Gene

  filters = {
    'symbol': [ops.Exact, ops.Startswith],
    'names': [ops.IContains,],
    'description': [ops.IContains,]
  }

class miRNAGeneTargetComplexResource(Resource):
  document = miRNAGeneTargetComplex
  related_resources = {
    'gene': GeneResource
  }

class miRNAResource(SymbolicResource):
  document = miRNA

  related_resources = {
    'targets': miRNAGeneTargetComplexResource,
    'host': GeneResource,
  }

  filters = {
    'symbol': [ops.Exact, ops.Startswith],
  }
