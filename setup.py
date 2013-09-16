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
        "cdiff==0.9.2"
    ],

    dependency_links = [
        "https://github.com/ymattw/cdiff/archive/master.zip#egg=cdiff-0.9.2",
    ],

    author = "AR",
    description = ("pygrit intends to provide a minimal"
                   "python port from ruby grit."),
    url = "https://github.com/aleiphoenix/pygrit"
)
