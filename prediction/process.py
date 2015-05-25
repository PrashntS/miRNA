#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import signal

from miRNA_map import miRNA_map

from subprocess import call
call(["terminal-notifier -sound default -message \"Done\""], shell = True)