#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
import requests

ensembl_session = requests.Session()
headers = {
  'User-agent': (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36'
    ' (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
  ),
  'accept': 'application/json',
}

def ensembl_sequence(emblid, **kwargs):
  access_url = 'http://rest.ensembl.org/sequence/id/{0}?'.format(emblid)
  parameters = {
    'type': 'cdna',
    'multiple_sequences': 1,
  }
  for k, v in parameters.items():
    access_url += '{0}={1};'.format(k, v)

  r = ensembl_session.get(access_url, headers=headers)
  kwargs['doc'] = {
    'emblid': emblid,
    'fasta': r.json(),
    'origin': access_url,
  }
  return kwargs
