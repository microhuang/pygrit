# -*- coding: utf-8 -*-
import re
from .commit import Commit
from .git import Git

class Repo():

    def __init__(self, path, root_ref='master', bare=False):
        self.root_ref = root_ref or 'master'
        self.path = path
        self.git = Git(self.path)

    def commit(self, commit_id):
        # TODO: commit_id should also allow refs name, branch, tag
        if not re.match(r"[0-9a-fA-F]{40}", commit_id):
            raise NotImplementedError("not support refs name currenly.")
        result = self.git.get_commit(commit_id)
        commit = self._decorate_commit(result)
        commit.repo = self
        return commit

    def _decorate_commit(self, commit, ref=None):
        return Commit(commit, ref)
