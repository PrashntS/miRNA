#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
import json

from packrat.config import CATALOGUE

def get_json_dict(path):
  with open(path, 'r') as fl:
    dc = json.load(fl)
  return dc

catalogue = get_json_dict(CATALOGUE)
