#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam

from miriam.alchemy.rank import Tissue
#from miriam.stats.rank import Ranking

t=Tissue('emtab2919-liver')
#m=Ranking(t)
#r=m.functional_bumps()

from miriam.stats.rank import Frames

fr = Frames()
print(fr.merge_expression(t))

