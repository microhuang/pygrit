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

    def head(self):
        """
        return the current head
        """
        return Head.current(self)

    def set_head(self, head):
        """
        set head

        Args:
            head: is the head to set
        """
        try:
            self.git.symbolic_ref("HEAD", "refs/heads/%s" % head,
                                  raise_error=True)
            return True
        except OSError:
            import traceback
            logger.error(traceback.format_exc())
            return False

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
        """
        The Commit object for the specified id

        Args:
            id: is the SHA1 identifier of the commit

        Returns:
            Grit::Commit (baked)
        """
        options = {'max_count': 1}
        commits = Commit.find_all(self, commit_id, **options)
        if len(commits) > 0:
            return commits[0]

    def commits(self, start='master', max_count=10, skip=0):
        """
        An array of Commit object representing the history of a given ref/commit

        Args:
            start is the branch/commit name (default 'master')
            max_count: is the maximum number of commits to return (default 10, use False for all)
            skip: is the number of commits to skip (default 0)

        Returns:
            Grit::Commit[]
        """
        return Commit.find_all(self, start, max_count=max_count, skip=skip)

    def log(self, commit='master', path=None, **options):
        """
        The commit log for a treeish

        Returns:
            pygrit.commit.Commit[]
        """
        options['pretty'] = 'raw'
        if path:
            arg = [commit, '--', path]
        else:
            arg = [commit]
        commits = self.git.log(*arg, **options)
        return Commit.list_from_string(self, commits)

    def __repr__(self):
        return "<pygrit.repo.Repo %s>" % self.path
