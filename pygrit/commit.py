# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from io import StringIO
from collections import deque
from datetime import datetime
import re

from cdiff import PatchStream, DiffParser

from pygrit import logger
from pygrit.actor import Actor
from pygrit.diff import Diff
from pygrit.ext import encode
from pygrit.tree import Tree
from pygrit.utils.lazy import Lazy, lazyprop
from pygrit.utils.wrappers import cached


class Commit(Lazy):

    def __init__(self, repo, id, parents, tree, author,
                 authored_timestamp, authored_offset, committer,
                 committed_timestamp,committed_offset, message):
        """
        Instantiate a new Commit

        Args:
            id: is the id of the commit
            parents: is an array of commit ids
            tree: is the correspdonding tree id
            author: is the author string
            authored_timestamp: is the authored_timestamp
            authored_offset: is the authored_offset (seconds)
            committer: is the committer string
            committed_timestamp: is the committed_timestamp
            committed_offset: is the committed_offset (seconds)
            message: is the message string

        Returns:
            pygrit.commit.Commit (baked)
        """
        super(Commit, self).__init__()
        self._diffs = None

        self.repo = repo
        self.id = id
        self._old_message = b"\n".join(message)
        self._old_short_message = b''
        for line in message:
            if line:
                self._old_short_message = line
                break
        self._parents = map(lambda id: Commit.create(repo, id=id), parents)
        self._author = author
        self._authored_timestamp = int(authored_timestamp)
        self._authored_offset = self._convert_offset(authored_offset)
        self._committer = committer
        self._committed_timestamp = int(committed_timestamp)
        self._committed_offset = self._convert_offset(committed_offset)
        self._tree = Tree.create(repo, id=tree)

    @lazyprop
    def parents(self):
        return self._parents

    @lazyprop
    def tree(self):
        return self._tree

    @lazyprop
    def author(self):
        return self._author

    @lazyprop
    def authored_timestamp(self):
        return self._authored_timestamp

    @lazyprop
    def authored_offset(self):
        return self._authored_offset

    @lazyprop
    def committer(self):
        return self._committer

    @lazyprop
    def committed_timestamp(self):
        return self._committed_timestamp

    @lazyprop
    def committed_offset(self):
        return self._committed_offset

    @lazyprop
    def message(self):
        return self._message

    @property
    def _message(self):
        return encode(self._old_message)

    @lazyprop
    def short_message(self):
        return encode(self._short_message)

    @property
    def _short_message(self):
        return encode(self._old_short_message)

    @property
    def authored_datetime(self):
        return datetime.fromtimestamp(self.authored_timestamp)

    @property
    def committed_datetime(self):
        return datetime.fromtimestamp(self.committed_timestamp)

    @property
    def timestamp(self):
        return self.committed_timestamp

    @property
    def datetime(self):
        return datetime.fromtimestamp(self.committed_timestamp)

    @property
    def sha(self):
        return self.id

    @property
    def short_id(self, length=10):
        return self.id[:length]

    @property
    @cached
    def diffs(self):
        if len(self.parents) > 0:
            parent = self.parents[0].id
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

    def lazy_source(self):
        return self.find_all(self.repo, self.id, max_count=1)[0]

    @staticmethod
    def create(repo, **attrs):
        """
        create a unbaked Commit instance, without init routine
        """
        commit = Commit.__new__(Commit)
        commit.repo = repo
        for k in attrs:
            setattr(commit, k, attrs[k])
        setattr(commit, "_loaded", False)
        return commit

    @staticmethod
    def find_all(repo, ref, **options):
        """
        Find all commits matching the given criteria

        Args:
            repo: is the Repo
            ref: is the ref from which to begin (SHA1 or name) or None for --all
            options:
                max_count: is the maximum number of commits to fetch
                skip: is the number of commits to skip

        Returns:
            pygrit.commit.Commit[] (baked)
        """
        options['pretty'] = 'raw'
        if ref:
            output = repo.git.rev_list(ref, **options)
        else:
            options['all'] = True
            output = repo.git.rev_list(ref, **options)

        return Commit.list_from_string(repo, output)

    @staticmethod
    def list_from_string(repo, text):
        """
        Parse out commit information into an array of baked Commit objects

        Args:
            repo: is the Repo
            text: is the text output from the git command (raw format)

        Returns:
            pygrit.commit.Commit[] (baked)
        """
        text_gpgless = re.sub(r'gpgsig -----BEGIN PGP SIGNATURE-----[\n\r]'
                              r'(.*[\n\r])*? -----END PGP SIGNATURE-----[\n\r]',
                              "", text)
        from pygrit import logger
        lines = deque(text_gpgless.split(b"\n"))
        commits = list()

        while len(lines) > 0:
            # Skip all garbage unless we get real commit
            while len(lines) > 0 and \
                  (not re.match(r'^commit [a-zA-Z0-9]*$', lines[0])):
                lines.popleft()
            if len(lines) <= 0:
                break

            parts = lines.popleft().split()
            id = parts[len(parts) - 1]
            parts = lines.popleft().split()
            tree = parts[len(parts) - 1]

            parents = list()
            while re.match(r'^parent', lines[0]):
                parts = lines.popleft().split()
                parents.append(parts[len(parts) - 1])

            author_line = lines.popleft()
            while not re.match(r'^committer', lines[0]):
                author_line += lines.popleft()
            author, \
                authored_timestamp, authored_offset = Commit.actor(author_line)

            committer_line = lines.popleft()
            while lines[0] and (not re.match(r'^encoding', lines[0])) and \
                  (not re.match(r'^encoding', lines[0])):
                committer_line += lines.popleft()
            committer, \
                committed_timestamp, \
                committed_offset = Commit.actor(committer_line)

            committer = committer

            # not using here though
            if re.match(r'^encoding', lines[0]):
                parts = lines.popleft().split()
                encoding = parts[len(parts) - 1]

            # Skip signature and other raw data
            while re.match(r'^ ', lines[0]):
                lines.popleft()

            lines.popleft()

            message_lines = list()
            if len(lines) > 0:
                while re.match(r'^ {4}', lines[0]):
                    # TODO: locale get from ENV
                    message_lines.append(lines.popleft()[4:])

            while len(lines) > 0 and lines[0] == "":
                lines.popleft()

            commit = Commit(repo, id, parents, tree, author, authored_timestamp,
                            authored_offset, committer, committed_timestamp,
                            committed_offset, message_lines)
            commits.append(commit)

        return commits

    @staticmethod
    def actor(line):
        m = re.match(r'.+? (.+) (\d+) (.*)$', line)
        if m:
            return [Actor.from_string(m.group(1)), m.group(2), m.group(3)]

    def _convert_offset(self, offset):
        """
        convert offset string to minutes

        Args:
            offset: is the offset string, like '+0800'

        Returns:
            offset minutes, for example: -480
        """
        direction = offset[0]
        hours = int(offset[1:3])
        mins = int(offset[3:5])
        if direction == "-":
            return (hours * 60 + mins) * -1
        return hours * 60 + mins

    def __repr__(self):
        return "#<pygrit.commit.Commit \"%s\">" % self.id
