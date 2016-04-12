#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
# 28 Feb 2016

from minion import mincli
from packrat import db

from miriam import logger
from miriam.graph import g

@mincli.command("feb28")
def routine():
  """
  Fix the inconsistencies in the Database.
  """
  genes = g.genes
  gene_db = db['ncbi_gene_docs']
  for gene in genes:
    count = gene_db.count({"gene_id": gene})
    if count is not 1:
      logger.debug("FixMe: {0};\tCount: {1}".format(gene, count))

