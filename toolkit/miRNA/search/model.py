#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID, STORED, NUMERIC, NGRAM
from whoosh.analysis import StemmingAnalyzer, NgramFilter

ngt = NgramFilter(minsize = 2, maxsize = 20)

class PolynucleotideSchema(SchemaClass):
  id = ID(stored = True, unique = True)
  symbol = NGRAM(minsize = 2, maxsize = 20)
  description = TEXT(field_boost = 5,
                     analyzer = StemmingAnalyzer(),
                     spelling = True)
  degree = NUMERIC(sortable = True)
  kind = KEYWORD()

class NotIndexedException(Exception):
  message = "The Index hasn't been created."
