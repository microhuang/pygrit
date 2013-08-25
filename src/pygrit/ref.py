# -*- coding: utf-8 -*-
from pygrit import logger
from pygrit.commit import Commit


class Ref(object):

    def __init__(self, name, commit):
        self.name = name
        self.commit = commit

    @classmethod
    def _prefix(klass):
        name = klass.__name__.lower()
        return "refs/%ss" % name

    @classmethod
    def find_all(klass, repo, **options):
        refs = repo.git.refs(options, klass._prefix())
        def map_ref(ref):
            name, id = ref.split(' ')
            commit = Commit.create(repo, id=id)
            return klass(name, commit)
        return map(map_ref, refs.split("\n"))

    def __repr__(self):
        classname = self.__class__.__name__.lower()
        return "<%s %s>" % (classname, self.name)


class Head(Ref):
    pass

class Remote(Ref):
    pass
