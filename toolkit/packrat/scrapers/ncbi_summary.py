#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
import requests
import xmltodict

user_agent = {'User-agent':
  ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36')
  (' (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')
}

def ncbi_search_id(symbol):
  access_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
  parameters = {
    'db': 'gene',
    'term': '{0}[GENE] AND "Homo Sapiens"[ORGN]'.format(symbol)
  }
  r = requests.get(access_url, params=parameters, headers=user_agent)
  d = xmltodict.parse(r.text)
  return d['eSearchResult']['IdList']['Id']

def _find_key_in_odict(hook, key, val):
  for dat in hook:
    if dat[key] == val:
      return dat

def ncbi_get_summary(eid):
  access_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
  parameters = {
    'db': 'gene',
    'id': eid,
    'format': 'xml',
  }
  r = requests.get(access_url, params=parameters, headers=user_agent)
  d = xmltodict.parse(r.text)
  xdoc = d['Entrezgene-Set']['Entrezgene']

  symbol = xdoc['Entrezgene_gene']['Gene-ref']['Gene-ref_locus']
  name = xdoc['Entrezgene_gene']['Gene-ref']['Gene-ref_desc']
  summary = xdoc['Entrezgene_summary']
  syn = xdoc['Entrezgene_gene']['Gene-ref']['Gene-ref_syn']['Gene-ref_syn_E']
  ensembl_id = _find_key_in_odict(
    xdoc['Entrezgene_gene']['Gene-ref']['Gene-ref_db']['Dbtag'],
    key='Dbtag_db',
    val='Ensembl'
  )['Dbtag_tag']['Object-id']['Object-id_str']
  ncbi_id = xdoc['Entrezgene_track-info']['Gene-track']['Gene-track_geneid']
  prot_ref_hook = xdoc['Entrezgene_prot']['Prot-ref']['Prot-ref_name']
  prot_refs = prot_ref_hook['Prot-ref_name_E']

  prop_hook = xdoc['Entrezgene_properties']['Gene-commentary']

  val_get = lambda x: x['Gene-commentary_source']['Other-source']

  func_hook = prop_hook[2]['Gene-commentary_comment']['Gene-commentary'][0]
  func_list = func_hook['Gene-commentary_comment']['Gene-commentary']
  functions = [val_get(_)['Other-source_anchor'] for _ in func_list]

  proc_hook = prop_hook[2]['Gene-commentary_comment']['Gene-commentary'][1]
  proc_list = proc_hook['Gene-commentary_comment']['Gene-commentary']
  processes = [val_get(_)['Other-source_anchor'] for _ in proc_list]

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

  return out_dict
