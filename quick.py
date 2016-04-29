#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam

from miriam.alchemy.rank import Tissue
from miriam.stats.rank import Ranking

t=Tissue('emtab2919-liver')
m=Ranking(t)
r=m.functional_bumps()
