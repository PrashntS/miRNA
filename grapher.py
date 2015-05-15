#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import networkx as nx
from miRNA_map import miRNA_map
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite

class Routines(object):
    def export_gexf():
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

    def build_stats():
        count_v = []
        for rna, target in miRNA_map.items():
            count_v.append((rna, len(set(target))))

        print(sorted(count_v, key = lambda x: x[1]))

if __name__ == "__main__":
    Routines.build_stats()