#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import signal

from miRNA_map import miRNA_map

miRNA_ID_Store   = {}
gene_ID_Store    = {}
prediction_Store = {}
skipped_list     = []

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

def init():
    """
    Loads the cached files.
    """
    if os.path.isfile("miRNA_ID_Store.json"):
        with open("miRNA_ID_Store.json", "r") as minion:
            miRNA_ID_Store = json.loads(minion.read())

    if os.path.isfile("gene_ID_Store.json"):
        with open("gene_ID_Store.json", "r") as minion:
            gene_ID_Store = json.loads(minion.read())

    if os.path.isfile("prediction_Store.json"):
        with open("prediction_Store.json", "r") as minion:
            prediction_Store = json.loads(minion.read())

    if os.path.isfile("skipped_list.json"):
        with open("skipped_list.json", "r") as minion:
            skipped_list = json.loads(minion.read())


def die():
    with open("miRNA_ID_Store.json", "w") as minion:
        minion.write(json.dumps(miRNA_ID_Store))
    with open("gene_ID_Store.json", "w") as minion:
        minion.write(json.dumps(gene_ID_Store))
    with open("prediction_Store.json", "w") as minion:
        minion.write(json.dumps(prediction_Store))
    with open("skipped_list.json", "w") as minion:
        minion.write(json.dumps(skipped_list))

    print("Wrote all the files. Exiting.")

def routine():
    global prediction_Store, skipped_list
    count_miRNA_done = 0
    count_miRNA_total = len(miRNA_map)
    for miRNA, target_genes in miRNA_map.items():
        count_miRNA_done += 1
        count_gene_total = len(target_genes)
        count_gene_done  = 0

        prediction_Store[miRNA] = {}

        for gene in target_genes:
            count_gene_done += 1
            print("Retrieving Prediction for ({0}, {1}). Progress: Gene - ({2}/{3}); miRNA - ({4}/{5})".format(miRNA, gene, count_gene_done, count_gene_total, count_miRNA_done, count_miRNA_total))
            
            if (miRNA in prediction_Store) and (gene in prediction_Store[miRNA]):
                pass
            else:
                try:
                    prediction_Store[miRNA] = prediction(miRNA, gene)
                except Exception as e:
                    skipped_list.append([miRNA, gene, str(e)])

def signal_handler(signal, frame):
    print('\nEnding Prematurely after Dumping retrieved data. Please Wait.')
    die()
    exit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    init()
    routine()
    die()