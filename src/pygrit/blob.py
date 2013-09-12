# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mimetypes
import re
from pygrit.utils.wrappers import cached

class Blob(object):

    DEFAULT_MIME_TYPE = 'text/plain'
    UNKNOWN_TYPE = 'unknown'

    @staticmethod
    def create(repo, **attrs):
        """
        Create an unbaked Blob containing just the specified attributes

        Args:
            repo: is the Repo
            attrs: is a dict of instance variable data

        Returns:
            pygrit.blob.Blob (unbaked)
        """
        blob = Blob.__new__(Blob)
        blob.repo = repo
        for k in attrs:
            setattr(blob, k, attrs[k])
        # setattr(blob, "_loaded", False)
        return blob

    @staticmethod
    def blame(repo, commit, file):
        """
        The blame information for the given file at the given commit

        Returns:
            list: [pygrit.commit.Commit, list: [<line>]]
        """
        raise NotImplementedError()

    @property
    def size(self):
        raise NotImplementedError()

    @property
    @cached
    def data(self):
        return self.repo.git.cat_file(self.id, p=True)

    @property
    def mime_type(self):
        mimetypes.init()
        try:
            _ = re.match(r'.+(\.[^\.]+)', self.name)
            if _:
                return mimetypes.types_map[m.group(1)]
            else:
                return Blob.UNKNOWN_TYPE
        except:
            return Blob.UNKNOWN_TYPE

    def __repr__(self):
        return "#<pygrit.blob.Blob %s>" % self.id
