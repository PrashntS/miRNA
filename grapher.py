#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import networkx as nx
from miRNA_map import miRNA_map
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite

G = nx.Graph()

count = 0

for rna, target in miRNA_map.items():
    G.add_node(rna)
    G.add_nodes_from(target)
    for gene in target:
        G.add_edge(rna, gene)
    count += 1


c = bipartite.color(G)
nx.set_node_attributes(G, 'bipartite', c)
nx.write_gexf(G,"test_massive_color.gexf")
