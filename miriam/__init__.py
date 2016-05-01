#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import hug
import pecan_mount
import static

from miriam._version import current
from miriam._config import static_root
from packrat import db, psql


@hug.get('/', versions=current)
def get_root():
  return {
    'success': True
  }

from miriam.api import rank as rank_api
from miriam.api import computed as computed_api

@hug.extend_api('/rank')
def mount_rank():
  return [rank_api]

@hug.extend_api('/computed')
def mount_rank():
  return [computed_api]

pecan_mount.tree.graft(__hug_wsgi__, '/api')
pecan_mount.tree.graft(static.Cling(static_root), '/')

api = pecan_mount.tree
