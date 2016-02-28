#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask_restful import Resource, reqparse

from miRNA import logger

from miRNA.alchemy.docs import MiRNA, Gene
from miRNA.search.indexer import Indexer
from miRNA.search.model import query_parser

ix = Indexer.get_index()
parser = query_parser()

class SearchController(Resource):

  def args(self):
    parser = reqparse.RequestParser()
    parser.add_argument('q', type = str, required = True)
    parser.add_argument('page', type = int, default = 1)
    return parser.parse_args()

  def get(self):
    swag = self.args()
    q = swag.get('q')
    page = swag.get('page')

    with ix.searcher() as s:
      query = parser.parse(q)
      results = s.search_page(query, page)

      collec = lambda x: Gene if x['kind'] == 'Gene' else MiRNA
      repr_doc = lambda x: collec(x)(x['id']).repr

      return {
        'data': list(map(repr_doc, results)),
        'len': results.pagecount,
        'total': results.total,
        'page': page,
      }
