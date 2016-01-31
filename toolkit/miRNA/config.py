#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import logging
from logging.handlers import RotatingFileHandler

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

WHOOSH_INDEX = "/data/whooshindex"

_formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")

HANDLER = RotatingFileHandler('/data/mirna.log',
                              maxBytes = 10000,
                              backupCount = 1)
HANDLER.setLevel(logging.DEBUG)
HANDLER.setFormatter(_formatter)
