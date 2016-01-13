#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask_admin import Admin
from flask_admin.contrib.mongoengine import ModelView

from miRNA.polynucleotide.model import Gene, miRNA

from miRNA import app

admin = Admin(app, name = 'miRNA Toolbox')

admin.add_view(ModelView(Gene))
admin.add_view(ModelView(miRNA))
