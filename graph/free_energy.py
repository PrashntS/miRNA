#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

from miRNA_map import miRNA_map


def routine():

    miRNA_ID_URI = "http://mirmap.ezlab.org/app/remote/mirna?query={0}&run=1"
    gene_ID_URI  = "http://mirmap.ezlab.org/app/remote/gene?query=dusp&run=1"

    prediction_URI = "http://mirmap.ezlab.org/app/remote/db"

    data = {
        'json_request': {  
            "queries":[  
                {  
                    "run": 1,
                    "mirna": 11021,
                    "gene": 14925
                }
            ],
            "valuesFormat":" raw",
            "valuesLevel": "pair",
            "withSequence": True
        }
    }

