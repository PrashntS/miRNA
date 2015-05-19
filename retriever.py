#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

from miRNA_map import miRNA_map
from map_reverse import miRNA_reverse
from one_degree_mirna_mirna_map import one_degree_map
from miRNA_Sequences import sequence_lookup

def get_gene_summary_homo_sapiens(gene_name):
    URL = "http://www.ncbi.nlm.nih.gov"
    payload = {'term': '({0}) AND "Homo sapiens"[porgn:__txid9606]'.format(gene_name) }
    search_request = requests.get(URL + "/gene", params = payload, timeout = 32)
    gene_dat = BeautifulSoup(search_request.text.encode())
    gene_url = search_request.url

    try:
        gene_url = URL + gene_dat.find("td", {"class": "gene-name-id"}).a.attrs['href']
    except Exception:
        pass

    gene_request = requests.get(gene_url, timeout = 32)
    summary = BeautifulSoup(gene_request.text.encode())

    head = summary.find("dl").find_all('dt')
    data = summary.find("dl").find_all('dd')

    saved_summary = {}

    saved_summary['FASTA_URL'] = URL + summary.find("a", {"title": "Nucleotide FASTA report"}).attrs['href']
    saved_summary['Data_URL'] = gene_request.url

    for i in range(0, max(len(head), len(data))):
        if "Symbol" in head[i].text:
            saved_summary['symbol'] = data[i].find(text=True, recursive=False)
        elif "Name" in head[i].text:
            saved_summary['name'] = data[i].find(text=True, recursive=False)
        elif "Summary" in head[i].text:
            saved_summary['summary'] = data[i].text
        elif "Gene type" in head[i].text:
            saved_summary['type'] = data[i].text

    return saved_summary
