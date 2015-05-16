#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from pyquery import PyQuery as pq

from miRNA_map import miRNA_map
from map_reverse import miRNA_reverse
from one_degree_mirna_mirna_map import one_degree_map
from miRNA_Sequences import sequence_lookup

URL = "http://www.ncbi.nlm.nih.gov"

payload = {'term': '(CCND1) AND "Homo sapiens"[porgn:__txid9606]'}
r = requests.get(URL + "/gene", params = payload)
gene_url = URL + pq(pq(r.text.encode())(".gene-tabular-rprt").find(".gene-name-id").eq(0).html()).find('a').attr("href")

print(requests.get(gene_url).text())