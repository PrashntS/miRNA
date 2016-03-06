#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import hug

from pymongo import MongoClient

from miriam._version import current
from miriam._config import MONGO, mongo_db_name

client = MongoClient(**MONGO)
db = client[mongo_db_name]


@hug.get('/', versions=current)
def get_root():
  return {
    'success': True
  }
