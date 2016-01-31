#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
import requests
import logging

from huey import RedisHuey
from tinydb import TinyDB, Query

from packrat.config import HUEY, TINYDB

huey = RedisHuey(**HUEY)
db = TinyDB(TINYDB)

@huey.task(retries=50, retry_delay=3)
def scrape(url, scraper, eid, table):
  tb = db.table(table)
  q = Query()

  if not tb.contains(q.eid == eid):
    r = requests.get(url, timeout=(5, 30))
    doc = scraper(r.text)
    doc['eid'] = eid
    db.table(table).insert(doc)

  logging.info("Done: {0}".format(url))
