#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer

class PolynucleotideSchema(SchemaClass):
  symbol = ID(stored = True, unique = True, field_boost = 10)
  description = TEXT(field_boost = 5)

class NotIndexedException(Exception):
  message = "The Index hasn't been created."
