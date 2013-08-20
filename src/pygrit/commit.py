# -*- coding: utf-8 -*-
from StringIO import StringIO

from cdiff import PatchStream, DiffParser

from .diff import Diff
from .utils.wrappers import cached



class DiffEx(object):
    pass

class Commit:

    def __init__(self, raw_commit, head=None):
        if not raw_commit:
            raise StandardError("None as raw commit passwd")

        self._init_from_raw(raw_commit)
        self._diffs = None

        self.head = head
        self.repo = None

    def _init_from_raw(self, raw_commit):
        """
        init from result of Git.get_commit(), a dict
        """
        self._raw_commit = raw_commit
        self.id = raw_commit['id']
        self.message = raw_commit['message']
        self.authored_date = raw_commit['authored_timestamp']
        self.committed_date = raw_commit['committed_timestamp']
        self.author_name = raw_commit['author_name']
        self.author_email = raw_commit['author_email']
        self.committer_name = raw_commit['committer_name']
        self.committer_email = raw_commit['committer_email']
        self.parents_id = map(lambda x: x, raw_commit['parents'])

    def __repr__(self):
        return "<gitcorp_git.commit.Commit %s>" % self.id

    @property
    def sha(self):
        return self.id

    @property
    def short_id(self, length=10):
        return self.id[:length]

    @property
    @cached
    def diffs(self):
        parent = self.parents_id[0]
        raw_diff = self.repo.git.get_diff(parent, self.id)

        diff_hdl = StringIO(raw_diff)
        stream = PatchStream(diff_hdl)
        diffs = DiffParser(stream).get_diff_generator()

        result = list()
        for diff in diffs:
            result.append(Diff(diff))

        return result
