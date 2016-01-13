#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask_admin import Admin
from flask_admin.contrib.mongoengine import ModelView

from miRNA.polynucleotide.model import Gene, miRNA

from miRNA import app

admin = Admin(app, name = 'miRNA Toolbox')

class BaseView(ModelView):
  can_view_details = True
  column_searchable_list = ['symbol']
  column_filters = ['symbol']

admin.add_view(BaseView(Gene))
admin.add_view(BaseView(miRNA))
