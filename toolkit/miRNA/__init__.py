#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__, template_folder='static')
app.config.from_pyfile('config.py')

db = MongoEngine(app)

def create_app():
  @app.route('/')
  def home():
    return render_template('index.html')
