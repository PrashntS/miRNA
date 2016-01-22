#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from miRNA import rd

#: Nodes Store. Simply stores the Symbols
miRNA_nodes = rd.Set('miRNANodes')
gene_nodes  = rd.Set('geneNodes')

#: Edges. Edges are stored as List of Dicts
#: Multiple redundancy is provided as a trade-off between time and space
#1 miRNA --(Targets)---> Gene
#2 Gene  --(Produces)--> miRNA
#3 Gene  <-(Target of)-- miRNA
#4 miRNA <-(Product of)- Gene
#: Each of these Edges are implemented as Hashes of Touples.

miRNA_targets_genes   = rd.Hash('miRNATargetsGene')
gene_produces_mirna   = rd.Hash('GeneProducesmiRNA')
gene_target_of_mirna  = rd.Hash('GeneTargetOfmiRNA')
miRNA_product_of_gene = rd.Hash('miRNAProductOfGene')
