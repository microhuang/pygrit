# -*- coding: utf-8 -*-
from StringIO import StringIO
from datetime import datetime

from cdiff import PatchStream, DiffParser

from pygrit.diff import Diff
from pygrit.utils.wrappers import cached



class Commit(object):

    def __init__(self, raw_commit, head=None):
        if not raw_commit:
            raise StandardError("None as raw commit passwd")

        self._init_from_raw(raw_commit)
        self._diffs = None

        self.head = head
        self.repo = None

    @property
    def authored_datetime(self):
        return datetime.fromtimestamp(self.authored_timestamp)

    @property
    def committed_datetime(self):
        return datetime.fromtimestamp(self.committed_timestamp)

    @property
    def datetime(self):
        return self.committed_timestamp

    def _init_from_raw(self, raw_commit):
        """
        init from result of Git.get_commit(), a dict
        """
        self._raw_commit = raw_commit
        self.id = raw_commit['id']
        self.message = raw_commit['message']
        self.author_name = raw_commit['author_name']
        self.author_email = raw_commit['author_email']
        self.authored_timestamp = int(raw_commit['authored_timestamp'])
        self.authored_offset = int(raw_commit['authored_offset'])
        self.committer_name = raw_commit['committer_name']
        self.committer_email = raw_commit['committer_email']
        self.committed_timestamp = int(raw_commit['committed_timestamp'])
        self.committed_offset = int(raw_commit['committed_offset'])
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
        if len(self.parents_id) > 0:
            parent = self.parents_id[0]
            raw_diff = self.repo.git.get_diff(parent, self.id)
        else:
            raw_diff = self.repo.git.diff_tree(self.id, p=True, r=True,
                                               no_commit_id=True,
                                               encoding='utf-8', root=True)

        diff_hdl = StringIO(raw_diff)
        stream = PatchStream(diff_hdl)
        diffs = DiffParser(stream).get_diff_generator()

        result = list()
        for diff in diffs:
            result.append(Diff(diff))

        return result

    @staticmethod
    def create(repo, **attrs):
        """
        create a unbaked Commit instance, without init routine
        """
        commit = Commit.__new__(Commit)
        for k in attrs:
            setattr(commit, k, attrs[k])
        return commit
