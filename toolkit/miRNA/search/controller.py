#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask_restful import Resource, reqparse

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
      return {
        'data': [_['id'] for _ in results],
        'len': results.pagecount,
        'total': results.total,
        'page': page,
      }
