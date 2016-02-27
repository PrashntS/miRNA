#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import Flask, Blueprint
from flask_restful import Resource, Api

from miRNA.graph.controller import SubGraphController
from miRNA.search.controller import SearchController
from miRNA import app

api = Blueprint('api', __name__)

restful = Api(app, prefix = '/api')

restful.add_resource(SearchController, '/search')
restful.add_resource(SubGraphController, '/graph')
