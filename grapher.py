#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import networkx as nx
from miRNA_map import miRNA_map
from map_reverse import miRNA_reverse
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite
import json

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

    def build_stats_forward():
        count_v = []
        for rna, target in miRNA_map.items():
            count_v.append((rna, len(set(target))))

        print(sorted(count_v, key = lambda x: x[1]))

    def build_stats_reverse():
        count_v = []
        for rna, target in miRNA_reverse.items():
            count_v.append((rna, len(set(target))))

        print(sorted(count_v, key = lambda x: x[1]))

    def reverse_list():
        key_list = {}
        for rna, target in miRNA_map.items():
            for i in target:
                key_list[i] = []

        for rna, target in miRNA_map.items():
            for gene in target:
                key_list[gene].append(rna)

        with open("map_reverse.json", "w") as minion:
            minion.write(json.dumps(key_list, indent = 4))

if __name__ == "__main__":
    print(len(miRNA_reverse))