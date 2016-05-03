#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import json
from pybloomfilter import BloomFilter

from miriam.network import g

SOURCES = ['PharmGKB', 'KEGG', 'SMPDB', 'PID']
__genes__ = BloomFilter(20000, 0.0001)

for gene in g.genes:
  __genes__.add(gene)

out = []

with open('CPDB_pathways_genes-2.tab', 'r') as fl:
  headers = fl.readline()
  for line in fl:
    pathway, external_id, source, ls = line.split('\t')
    if source not in SOURCES:
      continue

    genes = list(filter(lambda x: x in __genes__, ls.strip().split(',')))
    if len(genes) < 2:
      continue

    genes.sort()
    out.append([source, external_id, genes])

out.sort(key=lambda x: x[0])
out.sort(key=lambda x: x[1])

with open('cpdb_filtered.json', 'w') as fl:
  json.dump(out, fl)
