# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pygrit.ext import encode

class Submodule(object):

    def __init__(self):
        pass

    @property
    def name(self):
        return encode(self.old_name)

    @staticmethod
    def create(repo, **attrs):
        submodule = Submodule.__new__(Submodule)
        for k in attrs:
            if k == 'name':
                setattr(submodule, 'old_name', attrs[k])
            else:
                setattr(submodule, k, attrs[k])
        return submodule

    @staticmethod
    def config(repo, ref='master'):
        raise NotImplementedError()

    def url(self):
        raise NotImplementedError()

    def __repr__(self):
        return "#<pygrit.submodule.Submodule %s>" % self.id
