#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from whoosh.fields import (SchemaClass, TEXT, KEYWORD, ID,
                           STORED, NUMERIC, NGRAM)
from whoosh.analysis import StemmingAnalyzer, NgramFilter

from whoosh import qparser
from whoosh.qparser import MultifieldParser

class PolynucleotideSchema(SchemaClass):
  id = ID(stored = True, unique = True)
  symbol = NGRAM(minsize = 2, maxsize = 20)
  description = TEXT(analyzer = StemmingAnalyzer(),
                     spelling = True)
  degree = NUMERIC(sortable = True)
  kind = KEYWORD(stored = True)

class NotIndexedException(Exception):
  message = "The Index hasn't been created."

def query_parser():
  parser = MultifieldParser(["symbol", "description", "kind"],
                            schema = PolynucleotideSchema())

  parser.remove_plugin_class(qparser.WildcardPlugin)
  parser.remove_plugin_class(qparser.FieldsPlugin)
  parser.add_plugin(qparser.FuzzyTermPlugin())
  return parser
