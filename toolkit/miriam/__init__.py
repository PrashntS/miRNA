#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import Flask, render_template
from flask_socketio import SocketIO, send as sock_send, emit
from walrus import Database as WalrusDB

from miriam.config import logging_handle, console_handle

app = Flask(__name__, template_folder='static')
app.config.from_pyfile('config.py')

walrus    = WalrusDB(**app.config.get('REDIS'))
memcache  = walrus.cache()

app.logger.handlers = [logging_handle, console_handle]
logger = app.logger

socketio  = SocketIO(app)


def create_app():
  from .api.controller import api

  app.register_blueprint(api, url_prefix = '/api')

  logger.info("App Started")

  @app.route('/')
  def home():
    return render_template('index.html')
