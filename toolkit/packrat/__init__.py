#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
import requests
import logging

from huey import RedisHuey
from pymongo import MongoClient

from packrat.config import HUEY, TINYDB

huey = RedisHuey(**HUEY)
db = MongoClient()['packrat']

@huey.task(retries=50, retry_delay=3)
def scrape(url, scraper, eid, table):
  tb = db[table]

  if not tb.find({'eid': eid}).count() > 0:
    r = requests.get(url, timeout=(5, 30))
    doc = scraper(r.text)
    doc['eid'] = eid
    tb.insert(doc)

  logging.info("Done: {0}".format(url))
