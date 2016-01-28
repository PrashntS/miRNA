#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import scrapy

class NCBI(scrapy.Spider):
  name = 'NCBI Gene'
  start_urls = ['']
