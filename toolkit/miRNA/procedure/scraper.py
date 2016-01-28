#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import asyncio
import aiohttp

from tqdm import tqdm
from pyquery import PyQuery as pq

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
    d = pq(dat.encode())

    s_dl = d("[id=summaryDl]").eq(0).children()
    i_pw = d(".geneinfo-subsec.infopathway").children()

    i_sec = pq(d(".gene-ontology.infosec").html()).find('tbody')
    funct = i_sec.eq(0).children()
    procs = i_sec.eq(1).children()

    protn = pq(d(".gene-general-protein-info").html()).find('dl')

    pw_gen = lambda x: {
      'name': x.children().eq(1).children().eq(0).text(),
      'desc': x.children().eq(1).children().eq(1).text(),
      'href': x.children().eq(0).attr('href'),
    }

    l_f = len(funct)
    l_p = len(procs)

    doc = {
      'full_name': s_dl.eq(3).text(),
      'lineage': s_dl.eq(15).text().split('; '),
      'alias': s_dl.eq(17).text().split('; '),
      'summary': s_dl.eq(19).text(),
      'pathways': [pw_gen(i_pw.eq(_)) for _ in range(len(i_pw))],
      'function': [funct.eq(_).children().eq(0).text() for _ in range(l_f)],
      'process': [procs.eq(_).children().eq(0).text() for _ in range(l_p)],
      'protein_info': {
        'name': protn.eq(0).children().eq(1).text(),
        'alias': [_.text for _ in protn.eq(1).children()[1:]]
      }
    }

    return doc

# ids = ['1026', 'CDKN2A', 'fhdnisjckoz']
# x = NCBIGene(ids)
# x.routine()
# print(x.storage)
