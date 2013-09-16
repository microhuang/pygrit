# -*- coding: utf-8 -*-
from __future__ import unicode_literals

class Submodule(object):

    def __init__(self):
        pass

    @staticmethod
    def create(repo, **attrs):
        submodule = Submodule.__new__(Submodule)
        for k in attrs:
            setattr(submodule, k, attrs[k])
        return submodule

    @staticmethod
    def config(repo, ref='master'):
        raise NotImplementedError()

    def url(self):
        raise NotImplementedError()

    def __repr__(self):
        return "#<pygrit.submodule.Submodule %s>" % self.id
