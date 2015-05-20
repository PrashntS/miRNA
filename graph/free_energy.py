#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

from miRNA_map import miRNA_map

miRNA_ID_URI = "http://mirmap.ezlab.org/app/remote/mirna?query={0}&run=1"
gene_ID_URI  = "http://mirmap.ezlab.org/app/remote/gene?query={0}&run=1"

