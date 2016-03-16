#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MiRiam
import hug

@hug.get('/')
def get_root():
  return 'Test'
