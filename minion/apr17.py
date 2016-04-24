#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
# 17 Apr 2016
import json
import datetime
import tqdm

from packrat import catalogue
from miriam.network import g
from miriam.alchemy.rank import TissueCollection
from miriam.stats.rank import Ranking

MOTIFKINDS = ['D1', 'T2', 'T3', 'T4', 'T6', 'T7']

if __name__ == '__main__':
  out = []
  mirna_scores = [0] * len(g.mirnas)
  gene_scores = [0] * len(g.genes)

  for tissue in tqdm.tqdm(TissueCollection()):
    ranks = Ranking(tissue)
    motifs = ranks.graph.motif
    mirnas_rnk = ranks.mirnas
    genes_rnk = ranks.genes
    out.append({
      'tissue': tissue.id,
      'mirnas': mirnas_rnk,
      'genes':  genes_rnk,
      'motif_counts': [(_, len(motifs[_])) for _ in MOTIFKINDS],
      'report': ranks.report,
    })
    mirna_scores = list(map(sum, zip(mirna_scores, mirnas_rnk)))
    gene_scores = list(map(sum, zip(gene_scores, genes_rnk)))

  mirna_scores = list(map(lambda x: x / len(out), mirna_scores))
  gene_scores = list(map(lambda x: x / len(out), gene_scores))

  with open('full_rpt.{0}.json'.format(datetime.datetime.now().isoformat()), 'w') as fl:
    json.dump(out, fl)

  with open('overlaps.{0}.json'.format(datetime.datetime.now().isoformat()), 'w') as fl:
    json.dump({
      'mirna': mirna_scores,
      'gene': gene_scores
    }, fl)
