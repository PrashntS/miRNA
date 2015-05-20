#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

from miRNA_map import miRNA_map

miRNA_ID_Store   = {}
gene_ID_Store    = {}
prediction_Store = {}

def _miRNA_ID(miRNA):
    """
    Returns the miRNA ID for given miRNA string.
    Caches the IDs in global data store.
    """
    global miRNA_ID_Store

    if miRNA in miRNA_ID_Store:
        return miRNA_ID_Store[miRNA]
    else:
        miRNA_ID_URI = "http://mirmap.ezlab.org/app/remote/mirna?query={0}&run=1".format(miRNA)
        data = requests.get(miRNA_ID_URI, timeout = 32).json()

        if 'items' not in data:
            raise ValueError("Malformed data returned for miRNA `{0}`.".format(miRNA))

        for item in data['items']:
            if item['name'] == miRNA:
                miRNA_ID_Store[miRNA] = item['id']
                return miRNA_ID_Store[miRNA]

        raise ValueError("miRNA `{0}` name not present is query results.".format(miRNA))

def _gene_ID(gene):
    """
    Returns the Gene ID for given Gene string.
    Caches the IDs in global data store.
    """
    global gene_ID_Store

    if gene in gene_ID_Store:
        return gene_ID_Store[gene]['id']
    else:
        gene_ID_URI  = "http://mirmap.ezlab.org/app/remote/gene?query={0}&run=1".format(gene)
        data = requests.get(gene_ID_URI, timeout = 32).json()

        if 'items' not in data:
            raise ValueError("Malformed data returned for gene `{0}`.".format(gene))

        for item in data['items']:
            if item['name'] == gene:
                gene_ID_Store[gene] = item
                return gene_ID_Store[gene]['id']

        raise ValueError("Gene `{0}` name not present is query results.".format(gene))

def prediction(miRNA, gene):
    """
    Retrieves the prediction data from mirmap.
    """
    prediction_URI = "http://mirmap.ezlab.org/app/remote/db"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    _data = {
        'json_request': json.dumps({  
            "queries":[  
                {  
                    "run": 1,
                    "mirna": _miRNA_ID(miRNA),
                    "gene": _gene_ID(gene)
                }
            ],
            "valuesFormat":" raw",
            "valuesLevel": "pair",
            "withSequence": True
        })
    }

    data = requests.post(prediction_URI, data = _data, params = headers, timeout = 32).json()

    if 'items' not in data:
        raise ValueError("Malformed data returned for prediction between miRNA `{0}`, and gene `{1}`.".format(miRNA, gene))

    if len(data['items']) > 0:
        return data['items'][0]

    raise ValueError("Gene `{0}` name not present is query results.".format(gene))


print(len(prediction("hsa-let-7a-3p", "ARMC8")))
