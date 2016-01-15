#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask.ext.mongorest import operators as ops
from flask.ext.mongorest.resources import Resource

from miRNA.polynucleotide.model import (Gene, miRNA,
                                        miRNAGeneTargetComplex,
                                        miRNAGeneTargetedByComplex)

class SymbolicResource(Resource):
  max_limit = 20
  rename_fields = {
    'searchable': 'q',
  }

  def get_object(self, pk, qfilter=None):
    qs = self.get_queryset()

    print(qs, pk, qfilter)
    if qfilter:
      qs = qfilter(qs)

    return qs.get(symbol = pk)

class miRNADoc(Resource):
  document = miRNA
  fields = ['id', 'symbol']

class miRNAGeneTargetedByComplexResource(Resource):
  document = miRNAGeneTargetedByComplex
  related_resources = {
    'miRNA': miRNADoc
  }

class GeneResource(SymbolicResource):
  document = Gene
  fields = ['id', 'symbol', 'description', 'names', 'transcript_count', 'targeted_by', 'host_of']

  related_resources = {
    'targeted_by': miRNAGeneTargetedByComplexResource,
    'host_of': miRNADoc,
  }

  filters = {
    'symbol': [ops.Exact, ops.Startswith],
    'names': [ops.IContains,],
    'description': [ops.IContains,],
    'q': [ops.IContains,]
  }


class GeneDoc(Resource):
  document = Gene
  fields = ['id', 'symbol']

class miRNAGeneTargetComplexResource(Resource):
  document = miRNAGeneTargetComplex
  fields = ['affinity', 'gene']
  related_resources = {
    'gene': GeneDoc
  }

class miRNAResource(SymbolicResource):
  document = miRNA
  fields = ['id', 'targets', 'host', 'mirbase_url', 'symbol']

  related_resources = {
    'targets': miRNAGeneTargetComplexResource,
    'host': GeneDoc,
  }

  filters = {
    'symbol': [ops.Exact, ops.Startswith],
  }
