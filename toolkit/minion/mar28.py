#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
# 28 Mar 2016
import networkx as nx
import json

from tqdm import tqdm

from miriam.stats.rank import get_ranks

"""Routine to generate a list of top 10 targeted genes and MiRNAs in tissues.

Output:
  > [Tissue: {'Genes': [...], 'MiRNA': [...], 'Report': {...}}]
"""

namespace = 'emtab2919'
tissues = [
  "adrenal_gland",
  "amygdala",
  "anterior_cingulate_cortex__ba24__of_brain",
  "aorta",
  "atrial_appendage_of_heart",
  "breast__mammary_tissue_",
  "caudate__basal_ganglia__of_brain",
  "cerebellar_hemisphere_of_brain",
  "cerebellum",
  "cerebral_cortex",
  "coronary_artery",
  # "cortex_of_kidney",
  # "ectocervix",
  # "esophagus_muscularis_mucosa",
  # "fallopian_tube",
  # "frontal_cortex__ba9_",
  # "gastroesophageal_junction",
  # "heart_left_ventricle",
  # "hippocampus",
  # "hypothalamus",
  # "leukemia_cell_line",
  # "liver",
  # "lung",
  # "minor_salivary_gland",
  # "mucosa_of_esophagus",
  # "nucleus_accumbens__basal_ganglia_",
  # "ovary",
  # "pancreas",
  # "pituitary_gland",
  # "prostate_gland",
  # "putamen__basal_ganglia_",
  # "sigmoid_colon",
  # "skeletal_muscle",
  # "skin_of_lower_leg",
  # "skin_of_suprapubic_region",
  # "spinal_cord__cervical_c_1_",
  # "spleen",
  # "stomach",
  # "subcutaneous_adipose_tissue",
  # "substantia_nigra",
  # "terminal_ileum_of_small_intestine",
  # "testis",
  # "thyroid",
  # "tibial_artery",
  # "tibial_nerve",
  # "transformed_fibroblast",
  # "transverse_colon",
  # "urinary_bladder",
  # "uterus",
  # "vagina",
  # "visceral__omentum__adipose_tissue",
  # "whole_blood",
]


if __name__ == '__main__':
  out = {}

  for tissue in tqdm(tissues):
    runner = get_ranks(tissue, namespace)
    g = runner.graphify()
    scores = nx.pagerank(g)

    key_func = lambda k: lambda x: scores[x] if g.node[x]['kind'] == k else -1

    out[tissue] = {
      'genes': sorted(scores, key=key_func('GEN'), reverse=True)[:10],
      'mirna': sorted(scores, key=key_func('MIR'), reverse=True)[:10],
      'rprts': runner.report
    }

  with open("runneroutfullxx.json", 'w') as f:
    json.dump(out, f, indent=2)
