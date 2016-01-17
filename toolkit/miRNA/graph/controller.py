#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import networkx as nx

from flask_restful import Resource, reqparse

from miRNA.polynucleotide.model import Gene, miRNA

class SubGraphController(Resource):
  def args(self):
    parser = reqparse.RequestParser()
    parser.add_argument('genes', type = str, action = 'append')
    parser.add_argument('mirna', type = str, action = 'append')
    return parser.parse_args()

  def get(self):
    swag = self.args()
    genes = self._gather(Gene, swag.get('genes'))
    mirna = self._gather(miRNA, swag.get('mirna'))

    return self._get(mirna, genes)

  def _gather(self, collection, arr):
    doc = []

    if not arr:
      return doc
    for sym in arr:
      try:
        doc.append(collection.objects.get(symbol = sym))
      except Exception:
        pass
    return doc

  def _get(self, imirna, igenes):
    in_mirna = set(imirna)
    in_genes = set(igenes)

    #: {Edge(miRNA -> Gene)}
    target_list = set()

    #: {Edge(Gene -> miRNA)}
    host_list   = set()

    miRNA_store = set()
    genes_store  = set()

    #: Save thyself!
    miRNA_store.update(in_mirna)
    genes_store.update(in_genes)

    def factory(_in_mirna, _in_genes):
      for mir in _in_mirna:
        #: Gather the targets of the miRNAs given
        targets = Gene.objects(targeted_by__miRNA=mir.id)

        genes_store.update(targets)
        target_list.update([(mir, _) for _ in targets])

        if mir.host:
          genes_store.add(mir.host)
          host_list.update([(mir.host, mir)])

      for gene in _in_genes:
        #: The miRNAs which targets the given one
        targeted_by = miRNA.objects(targets__gene=gene.id)
        miRNA_store.update(targeted_by)
        target_list.update([(_, gene) for _ in targeted_by])

        if gene.host_of:
          miRNA_store.add(gene.host_of)
          host_list.update([(gene, gene.host_of)])

    factory(in_mirna, in_genes)
    factory(miRNA_store.copy(), genes_store.copy())

    trn = lambda x: str(x)
    tre = lambda x: [str(x[0]), str(x[1])]

    return {
      'target_list': list(map(tre, target_list)),
      'host_list': list(map(tre, host_list)),
      'miRNA_store': list(map(trn, miRNA_store)),
      'genes_store': list(map(trn, genes_store)),
    }

