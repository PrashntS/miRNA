#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import networkx as nx

from flask_restful import Resource, reqparse

from miRNA.polynucleotide.model import Gene, miRNA

class SubGraphController(Resource):
  def get(self):

    #: Initial set containing the miRNAs from User
    in_mirna = set([miRNA.objects.get(symbol = 'hsa-let-7a-5p')])
    in_genes = set() #: Initial set containing the genes from User

    #: {Edge(miRNA -> Gene)}
    target_list = set()

    #: {Edge(Gene -> miRNA)}
    host_list   = set()

    miRNA_store = set()
    genes_store  = set()

    #: Save thyself!
    miRNA_store.update(in_mirna)
    genes_store.update(in_genes)

    def factory(in_mirna, in_genes):
      for mir in in_mirna:
        #: Gather the targets of the miRNAs given
        targets = Gene.objects(targeted_by__miRNA=mir.id)
        genes_store.update(targets)
        target_list.update([(mir, _) for _ in targets])

        if mir.host:
          miRNA_store.add(mir.host)
          host_list.update([(mir.host, mir)])

      for gene in in_genes:
        #: The miRNAs which targets the given one
        targeted_by = miRNA.objects(targets__gene=gene.id)
        miRNA_store.update(targeted_by)
        target_list.update([(_, gene) for _ in targeted_by])

        if gene.host_of:
          genes_store.add(gene.host_of)
          host_list.update([(gene, gene.host_of)])

    factory(in_mirna, in_genes)
    factory(miRNA_store.copy(), genes_store.copy())

    G = nx.DiGraph()
    G.add_nodes_from(miRNA_store)
    G.add_nodes_from(genes_store)

    G.add_edges_from(target_list)
    G.add_edges_from(host_list)

    dod = nx.convert.to_edgelist(G)

    print(nx.to_dict_of_dicts(G))

    convert = lambda x: (x[0].tinyrepr, x[1].tinyrepr)

    return list(map(convert, dod))
