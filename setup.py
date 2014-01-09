#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import find_packages, setup

version = '%s/VERSION' % os.path.abspath(os.path.dirname(__file__))
with open(version) as v:
    VERSION = v.readline().strip()

setup(
    name = "pygrit",
    version = VERSION,

    package_dir = {"": "src"},
    packages = find_packages("src"),

    entry_points = {},

    install_requires = [
        "chardet==2.1.1",
        "cdiff==0.9.3"
    ],

    author = "AR",
    description = ("pygrit intends to provide a minimal"
                   "python port from ruby grit."),
    url = "https://github.com/aleiphoenix/pygrit"
)
