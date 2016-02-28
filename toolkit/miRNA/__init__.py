#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import ZODB.config

from flask import Flask, render_template
from walrus import Database as WalrusDB

from miRNA.config import logging_handle, console_handle

app = Flask(__name__, template_folder='static')
app.config.from_pyfile('config.py')
app.logger.handlers = [logging_handle, console_handle]
logger = app.logger

walrus    = WalrusDB(**app.config.get('REDIS'))
memcache  = walrus.cache()

def create_app():
  from .api.controller import api

  app.register_blueprint(api, url_prefix = '/api')

  logger.info("App Started")

  @app.route('/')
  def home():
    return render_template('index.html')
