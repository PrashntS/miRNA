#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam

from miriam.stats.rank import Frame, Pipeline


fr  = Frame('emtab2919-liver')
pl  = Pipeline()
keq = pl.score_keq(fr.merged)
