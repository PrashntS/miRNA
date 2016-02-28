#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import Flask, Blueprint
from flask_restful import Resource, Api

from miriam.graph.controller import SubGraphController
from miriam.search.controller import SearchController
from miriam import app

api = Blueprint('api', __name__)

restful = Api(app, prefix = '/api')

restful.add_resource(SearchController, '/search')
restful.add_resource(SubGraphController, '/graph')
