#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import networkx as nx

from miRNA import rd

from walrus import Model, TextField, HashField

class miRNA(Model):
  database = rd
  symbol = TextField(primary_key = True)

  #: Outwards Edge
  targets = HashField()
  #: Inward Edge
  hosts = HashField()

class Gene(Model):
  database = rd
  symbol = TextField(primary_key = True)

  targeted_by = HashField()
  host_of = HashField()
