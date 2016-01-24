#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from miRNA import rd

#: Nodes Store. Simply stores the Symbols
miRNA_nodes = rd.Hash('miRNANodes')
gene_nodes  = rd.Hash('geneNodes')

#: Edges. Edges are stored as List of Dicts
#: Multiple redundancy is provided as a trade-off between time and space
#1 miRNA --(Targets)---> Gene  (Outward Edge)
#2 Gene  --(Produces)--> miRNA (Outward Edge)
#3 Gene  <-(Target of)-- miRNA (Inward Edge)
#4 miRNA <-(Product of)- Gene  (Inward Edge)
#: Each of these Edges are implemented as Hashes of Touples.

in_edge   = rd.Hash('InEdge')
out_edge  = rd.Hash('OutEdge')
