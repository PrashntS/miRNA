#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

# Redis Config
HUEY = {
  'name': 'miRNA-Huey',
  'host': 'localhost',
  'port': 6379,
  'db': 0,
}

MONGO = {
  'host': 'localhost',
  'port': 27017
}

ZEOCONF = ['localhost', 8090]

CATALOGUE = ("/repository/project/mir-to-gene/toolkit/"
             "data_dump/catalogue.json")
