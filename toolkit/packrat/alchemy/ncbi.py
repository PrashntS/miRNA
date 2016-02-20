#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
import requests
import xmltodict
import functools

user_agent = {'User-agent': (
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36'
  ' (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
)}

def _find_key_in_odict(hook, key, val):
  try:
    for dat in hook:
      if dat[key] == val:
        return dat
  except Exception:
    pass
  return {}

def rget(obj, attr, default=None):
  try:
    return functools.reduce(lambda x, y: x.get(y), [obj] + attr.split('.'))
  except (AttributeError, KeyError) as e:
    if default is not None:
      return default
    else:
      raise e

rgets = lambda o, a: rget(o, a, '')

def ncbi_search_id(symbol, **kwargs):
  access_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
  parameters = {
    'db': 'gene',
    'term': '{0}[GENE] AND "Homo Sapiens"[ORGN]'.format(symbol)
  }
  r = requests.get(access_url, params=parameters, headers=user_agent)
  d = xmltodict.parse(r.text)
  kwargs['eid'] = rget(d, 'eSearchResult.IdList.Id')
  return kwargs

def ncbi_get_summary(eid, **kwargs):
  access_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
  parameters = {
    'db': 'gene',
    'id': eid,
    'format': 'xml',
  }
  r = requests.get(access_url, params=parameters, headers=user_agent)
  d = xmltodict.parse(r.text)
  xdoc = rget(d, 'Entrezgene-Set.Entrezgene')

  symbol = rgets(xdoc, 'Entrezgene_gene.Gene-ref.Gene-ref_locus')
  name = rgets(xdoc, 'Entrezgene_gene.Gene-ref.Gene-ref_desc')
  summary = rgets(xdoc, 'Entrezgene_summary')
  syn = rgets(xdoc, 'Entrezgene_gene.Gene-ref.Gene-ref_syn.Gene-ref_syn_E')
  ensembl_id = rgets(_find_key_in_odict(
    rget(xdoc, 'Entrezgene_gene.Gene-ref.Gene-ref_db.Dbtag', []),
    key='Dbtag_db',
    val='Ensembl'
  ), 'Dbtag_tag.Object-id.Object-id_str')

  ncbi_id = rgets(xdoc, 'Entrezgene_track-info.Gene-track.Gene-track_geneid')
  prot_ref_hook = rgets(xdoc, 'Entrezgene_prot.Prot-ref.Prot-ref_name')
  prot_refs = rgets(prot_ref_hook, 'Prot-ref_name_E')

  prop_hook = rgets(xdoc, 'Entrezgene_properties.Gene-commentary')

  val_get = lambda x: rgets(x, 'Gene-commentary_source.Other-source')

  try:
    func_hook = rget(prop_hook[2], 'Gene-commentary_comment.Gene-commentary')[0]
    func_list = rget(func_hook, 'Gene-commentary_comment.Gene-commentary')
    functions = [val_get(_)['Other-source_anchor'] for _ in func_list]
  except Exception:
    functions = []

  try:
    proc_hook = rget(prop_hook[2], 'Gene-commentary_comment.Gene-commentary')[1]
    proc_list = rget(proc_hook, 'Gene-commentary_comment.Gene-commentary')
    processes = [val_get(_)['Other-source_anchor'] for _ in proc_list]
  except Exception:
    processes = []

  out_dict = {
    'symbol': symbol,
    'name': name,
    'summary': summary,
    'synonyms': syn,
    'ensemblid': ensembl_id,
    'ncbi_id': ncbi_id,
    'protein_ref': prot_refs,
    'functions': functions,
    'processes': processes
  }

  kwargs['doc'] = out_dict
  kwargs['symbol'] = symbol

  return kwargs
