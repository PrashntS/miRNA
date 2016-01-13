#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask.ext.mongorest import operators as ops
from flask.ext.mongorest.resources import Resource

from miRNA.polynucleotide.model import Gene, miRNA

class GeneResource(Resource):
    document = Gene

    filters = {
        'symbol': [ops.Exact, ops.Startswith],
    }
