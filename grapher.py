#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import networkx as nx
from miRNA_map import miRNA_map
import matplotlib.pyplot as plt

G = nx.Graph()

count = 0

for rna, target in miRNA_map.items():
    G.add_node(rna)
    G.add_nodes_from(target)
    for gene in target:
        G.add_edge(rna, gene)
    count += 1

nx.write_gexf(G,"test_massive.gexf")
