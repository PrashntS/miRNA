#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx
from miRNA_map import miRNA_map

G = nx.Graph()

for rna, target in miRNA_map.items():
    print(target)
    break
