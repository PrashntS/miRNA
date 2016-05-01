#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam

from miriam.stats.rank import Frame, Score_K_O_D


fr  = Score_K_O_D('emtab2919-liver')
rnk = fr.stack()
