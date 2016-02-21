#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
# 21 Feb 2016

from miRNA.graph import g
from miRNA.alchemy.expression import ExpressionAtlas

def routine_sorted_expr(namespace=None):
  """
  Tissue with minimum host genes expression.
  Comments: Small data helps to manually validate the outputs.
            Hence, a small dataset was chosen on the basis of expression
            level in tissues.
  """

  #: Get the hosts; These are the genes that are host of SOME (>=1) miRNA
  host_genes = [_ for _ in g.genes if len(g.host(_))]
  atlas = ExpressionAtlas(namespace)

  sum_dict = {k: 0 for k in atlas.tissues}

  #: Problem: Find Tissue with minimum host gene expressions.
  for tissue in atlas.tissues:
    atlas.tissue = tissue
    for gene in host_genes:
      try:
        sum_dict[tissue] += atlas.expr_level(gene)
      except ValueError as e:
        pass
    print(tissue)

  plis_do = lambda x: x(sum_dict, key=lambda x: sum_dict[x])
  min_key = plis_do(min)
  max_key = plis_do(max)

  suml = [(k, v) for k, v in sum_dict.items()]
  suml.sort(key=lambda x:x[1])

  return {
    'sums': suml,
    'least': [min_key, sum_dict[min_key]],
    'max': [max_key, sum_dict[max_key]],
  }

def routine_tissue_exprs(tissue, namespace=None):
  """
  Expression level in a particular tissues, of the host genes.
  """

  host_genes = [_ for _ in g.genes if len(g.host(_))]
  atlas = ExpressionAtlas(namespace)
  atlas.tissue = tissue

  exprs = []

  for gene in host_genes:
    try:
      exprs.append((gene, atlas.expr_level(gene)))
    except ValueError:
      print(gene)
      pass

  exprs.sort(key=lambda x: x[1])

  return {
    'tissue': tissue,
    'namespace': atlas.namespace,
    'expressions': exprs
  }

