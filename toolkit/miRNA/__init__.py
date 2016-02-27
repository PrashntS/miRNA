#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import ZODB.config

from flask import Flask, render_template
from walrus import Database as WalrusDB

app = Flask(__name__, template_folder='static')
app.config.from_pyfile('config.py')

walrus    = WalrusDB(**app.config.get('REDIS'))
memcache  = walrus.cache()

def create_app():
  from .api.controller import api

  app.logger.addHandler(app.config.get('HANDLER'))
  app.register_blueprint(api, url_prefix = '/api')

  app.logger.info("App Started")

  @app.route('/')
  def home():
    return render_template('index.html')
