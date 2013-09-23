# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from pygrit import logger
from pygrit.blob import Blob
from pygrit.errors import InvalidObjectTypeError
from pygrit.ext import encode
from pygrit.submodule import Submodule
from pygrit.utils.lazy import Lazy, lazyprop


class Tree(Lazy):

    def __init__(self):
        super(Tree, self).__init__()

    @property
    def name(self):
        return encode(self.old_name)

    @staticmethod
    def create(repo, **attrs):
        tree = Tree.__new__(Tree)
        tree.repo = repo
        for k in attrs:
            if k == 'name':
                setattr(tree, 'old_name', attrs[k])
            else:
                setattr(tree, k, attrs[k])
        setattr(tree, "_loaded", False)
        return tree

    @staticmethod
    def construct(repo, treeish, paths=list()):
        # TODO: consider implement `git ls-tree` in pure python ?
        output = repo.git.ls_tree(treeish, *paths, raise_error=True)
        tree = Tree.__new__(Tree)
        tree.construct_initialize(repo, treeish, output)
        return tree

    def construct_initialize(self, repo, id, text):
        self.repo = repo
        self.id = id
        self._contents = list()

        for line in text.split(b"\n"):
            if line.strip():
                _ = self.content_from_string(repo, line.strip())
                self._contents.append(_)

        for i in range(self._contents.count(None)):
            self._contents.remove(None)

        return self

    @lazyprop
    def contents(self):
        return self._contents

    def lazy_source(self):
        return Tree.construct(self.repo, self.id, list())

    def content_from_string(self, repo, text):
        """
        Parse a content item and create the appropriate object

        Args:
            repo: is the Repo
            text: is the single line containing the items data in `git ls-tree` format

        Returns:
            pygrit.blob.Blob or pygrit.tree.Tree
        """
        _ = re.split(r'[\ \t]', text, 3) # 4 parts at most
        mode, ftype, id, name = _
        name = name.decode('string-escape').strip(b'"')
        if ftype == 'tree':
            return Tree.create(repo, id=id, mode=mode, name=name)
        elif ftype == 'blob':
            return Blob.create(repo, id=id, mode=mode, name=name)
        elif ftype == 'link':
            return Blob.create(repo, id=id, mode=mode, name=name)
        elif ftype == 'commit':
            return Submodule.create(repo, id=id, mode=mode, name=name)
        else:
            raise InvalidObjectTypeError(ftype)

    def find(self, file):
        """
        Find the named object in this tree's contents
        Equivalent to `/` function in Grit::Tree

        Example:
            Repo('/path/to/pygrit').tree.find('src')
            Repo('/path/to/pygrit').tree.find('setup.py')
        """
        if re.search(r'/', file):
            try:
                return reduce(lambda acc, x: acc.find(x), file.split("/"), self)
            except:
                pass
        else:
            for c in self.contents:
                if c.name == file:
                    return c

    def __repr__(self):
        return "#<pygrit.tree.Tree \"%s\">" % self.id
