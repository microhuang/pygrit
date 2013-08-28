# -*- coding: utf-8 -*-
import re

from pygrit import logger
from pygrit.commit import Commit


class Ref(object):

    def __init__(self, name, repo, commit_id):
        self.name = name
        self.commit_id = commit_id
        self.repo_ref = repo

    @property
    def commit(self):
        return self.get_commit()

    def get_commit(self):
        return Commit.create(self.repo_ref, id=self.commit_id)

    @classmethod
    def _prefix(klass):
        name = klass.__name__.lower()
        return "refs/%ss" % name

    @classmethod
    def find_all(klass, repo, **options):
        refs = repo.git.refs(options, klass._prefix())
        def map_ref(ref):
            name, id = ref.split(' ')
            return klass(name, repo, id)
        return map(map_ref, refs.split("\n"))

    def __repr__(self):
        classname = self.__class__.__name__.lower()
        return "<%s %s>" % (classname, self.name)


class Head(Ref):

    @staticmethod
    def current(repo, **options):
        head = repo.git.symbolic_ref('HEAD')
        m = re.match(r'refs\/heads\/(.*)', head)
        if m:
            head = m.group(1)
            id = repo.git.rev_parse('HEAD', **options)
            if id:
                id = id.strip()
            return Head(head, repo, id)

class Remote(Ref):
    pass
