#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

DEBUG       = True
SECRET_KEY  = 'super-secret'
HOST        = 'http://localhost:9000'
SERVE_HOST  = '0.0.0.0'
SERVE_PORT  = 9000
MEINHELD    = False
THREADED    = False

# MongoDB Config
MONGODB_DB      = 'mirna'
MONGODB_HOST    = 'localhost'
MONGODB_PORT    = 27017

# Redis Config
REDIS = {
  'host': 'localhost',
  'port': 6379,
  'db': 0,
}

ZODB_PATH = '/data/zodb/mirna.fs'
