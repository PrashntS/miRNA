#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import click
import meinheld

from flask.ext.script import Manager
from miRNA import create_app, app

manager = Manager(app)

@manager.command
def runserver():
  "Runs the App"
  create_app()
  if app.config['MEINHELD']:
    meinheld.listen((app.config['SERVE_HOST'],
                     app.config['SERVE_PORT']))
    meinheld.run(app)
  else:
    app.run(host     = app.config['SERVE_HOST'],
            port     = app.config['SERVE_PORT'],
            threaded = app.config['THREADED'])

@manager.command
def setup_db():
  from pymongo import MongoClient
  from miRNA.config import MONGODB_DB, MONGODB_HOST, MONGODB_PORT
  client = MongoClient(MONGODB_HOST, MONGODB_PORT)
  client.drop_database(MONGODB_DB)

if __name__ == "__main__":
  manager.run()
