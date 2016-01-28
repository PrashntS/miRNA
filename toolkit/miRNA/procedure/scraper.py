#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import asyncio
import aiohttp
from tqdm import tqdm

class Retriever(object):
  def __init__(self, ids):
    self.conn = aiohttp.connector.TCPConnector(limit=10)
    self.ids = ids
    self.missed = []
    self.storage = {}

  async def delegator(self, coros):
    for f in tqdm(asyncio.as_completed(coros), total=len(coros)):
      out_dat, _id, status = await f
      if status == 200:
        self.storage[_id] = self.callback(out_dat)
      else:
        self.missed.append(_id)

  async def _get(self, _id):
    uri = self.uri_gen(_id)
    ret = await aiohttp.request('GET', uri, connector=self.conn)
    return await ret.text(), _id, ret.status

  def routine(self):
    loop = asyncio.get_event_loop()
    tasks = [self._get(_) for _ in self.ids]
    loop.run_until_complete(self.delegator(tasks))

  def __del__(self):
    self.conn.close()

  def uri_gen(self, _id):
    return None

  def callback(self, dat):
    return None

class NCBIGene(Retriever):
  def uri_gen(self, _id):
    return 'http://www.ncbi.nlm.nih.gov/gene/{0}'.format(_id)

  def callback(self, dat):
    return dat[:100]

# ids = ['1026', 'CDKN2A', 'fhdnisjckoz']
# x = NCBIGene(ids)
# x.routine()
# print(x.storage, x.missed)
