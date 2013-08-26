# -*- coding: utf-8 -*-
import os
import re
from StringIO import StringIO

from cdiff import PatchStream, DiffParser

from pygrit import logger
from pygrit.commit import Commit
from pygrit.diff import Diff
from pygrit.errors import InvalidGitRepositoryError, NoSuchPathError
from pygrit.git import Git
from pygrit.ref import Head
from pygrit.utils.wrappers import cached



class Repo():

    def __init__(self, path, bare=False):

        epath = os.path.abspath(path)

        if os.path.exists("%s/.git" % epath):
            self.workding_dir = epath
            self.path = "%s/.git" % epath
            self.bare = False
        elif os.path.exists(epath) and (epath.endswith('.git') or bare):
            self.path = epath
            self.bare= True
        elif os.path.exists(epath):
            raise InvalidGitRepositoryError(epath)
        else:
            raise NoSuchPathError(epath)

        self.git = Git(self.path)

    @classmethod
    def init(klass, path, **options):
        """
        init a git dir

        Example:
            Repo.init('/var/git/myrepo.git')
            repo.init(bare=True)
        """
        if 'bare' not in options.keys():
            path += '/.git'
        git = Git(path)
        git.fs_mkdir('..')
        git.init(path)
        return klass(path)

    def remote_add(self, name, url):
        """
        add remote to git

        Example:
            repo.remote_add('upstream', 'ssh://git@github.com/aleiphoenix/pygrit')
        """
        self.git.remote("add", name, url)

    def remote_fetch(self, name):
        """
        fetch a added remote

        Example:
            repo.remote_fetch('upstream')
        """
        self.git.fetch(name)

    def heads(self):
        """
        return all heads (branches)
        """
        return Head.find_all(self)


    @cached
    def diff(self, a, b, raw=False):
        raw_diff = self.git.diff(a, b)
        if raw:
            return raw_diff

        if not raw_diff:
            return ''

        diff_hdl = StringIO(raw_diff)
        stream = PatchStream(diff_hdl)
        diffs = DiffParser(stream).get_diff_generator()

        result = list()
        for diff in diffs:
            result.append(Diff(diff))

        return result

    def merge_base(self, a, b):
        mb = self.git.merge_base(a, b)
        logger.debug("merge_base: %s" % mb)
        if mb:
            return mb.strip()

    def commit(self, commit_id):
        options = {'max_count': 1}
        return Commit.find_all(self, commit_id, **options)[0]

    def __repr__(self):
        return "<pygrit.repo.Repo %s>" % self.path
