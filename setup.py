#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import find_packages, setup

version = '%s/VERSION' % os.path.abspath(os.path.dirname(__file__))
with open(version) as v:
    VERSION = v.readline().strip()

setup(
    name = "pygrit",
    description = ("pygrit intends to provide a minimal"
                   "python port from ruby grit."),
    version = VERSION,
    url = "https://github.com/aleiphoenix/pygrit",
    author = "AR",
    author_email = "aleiphoenix@gmail.com",
    packages = ['pygrit'],
    platforms = 'any',
    install_requires = [
        "chardet==2.1.1",
        "cdiff==0.9.3"
    ],
    entry_points = {}
)
