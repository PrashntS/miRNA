#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.
# 17 Apr 2016
import json
import datetime

from packrat import catalogue
from miriam.network import g
from miriam.alchemy.rank import TissueCollection
from miriam.stats.rank import Ranking


if __name__ == '__main__':
  out = []
  for tissue in TissueCollection():
    ranks = Ranking(tissue)
    out.append([tissue.id, ranks.functional_impact(sorted=False)])
  with open('fnr.{0}.json'.format(datetime.datetime.now().isoformat()), 'w') as fl:
    json.dump(out, indent=2)
