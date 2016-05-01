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

CATALOGUE = ("/repository/project/mir-to-gene/"
             "data_dump/catalogue.json")

PGSQLU = 'postgresql://prashantsinha@localhost:5432/miriam'
