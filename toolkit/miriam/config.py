#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import logging
import os
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

DEBUG       = True
SECRET_KEY  = 'super-secret'
HOST        = 'http://localhost:9000'
SERVE_HOST  = '0.0.0.0'
SERVE_PORT  = int(os.environ.get("PORT", 9000))
THREADED    = False

REDIS = {
  'host': 'localhost',
  'port': 6379,
  'db': 0
}

WHOOSH_INDEX = "/data/whooshindex"

_formatter = logging.Formatter(
  "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
)

logging_handle = RotatingFileHandler('/data/mirna.log',
                              maxBytes = 10000,
                              backupCount = 1)
logging_handle.setLevel(logging.DEBUG)
logging_handle.setFormatter(_formatter)

console_handle = StreamHandler()
console_handle.setLevel(logging.DEBUG)
console_handle.setFormatter(_formatter)
