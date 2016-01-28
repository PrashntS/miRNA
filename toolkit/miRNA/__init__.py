#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine
import ZODB.config

app = Flask(__name__, template_folder='static')
app.config.from_pyfile('config.py')

db = MongoEngine(app)
zdb = ZODB.config.databaseFromURL('./miRNA/zeo.client.config').open()

def create_app():
  from .admin.controller import admin
  from .api.controller import api

  app.logger.addHandler(app.config.get('HANDLER'))
  app.register_blueprint(api, url_prefix = '/api')

  app.logger.info("App Started")

  @app.route('/')
  def home():
    print()
    return render_template('index.html')
