#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import hug
import pecan_mount
import static

from pymongo import MongoClient
from sqlalchemy import create_engine

from miriam._version import current
from miriam._config import mongo, mongo_db_name, static_root, psql_url

client  = MongoClient(**mongo)
db      = client[mongo_db_name]
psql    = create_engine(psql_url)

@hug.get('/', versions=current)
def get_root():
  return {
    'success': True
  }

from miriam.api import rank

@hug.extend_api('/rank')
def mount_rank():
  return [rank]

pecan_mount.tree.graft(__hug_wsgi__, '/api')
pecan_mount.tree.graft(static.Cling(static_root), '/')

api = pecan_mount.tree
