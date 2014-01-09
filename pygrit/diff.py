# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from StringIO import StringIO

from cdiff import PatchStream, DiffParser
from pygrit.ext import encode


class Diff:

    serialize_keys = ["diff", "old_path", "new_path", "old_mode", "new_mode",
                      "new_file", "deleted_file", "renamed_file",
                      "diff_with_lineno", "binary"]

    def __init__(self, raw_diff):
        self.raw_diff = raw_diff

        self._headers = None

        sk = dict()
        for s in self.serialize_keys:
            if s == 'new_path':
                sk['_new_path'] = None
            elif s == 'old_path':
                sk['_old_path'] = None
            else:
                sk[s] = None
        self.__dict__.update(sk)

        self._init_from_raw()

    @property
    def new_path(self):
        return encode(self._new_path.decode('string-escape'))

    @property
    def old_path(self):
        return encode(self._old_path.decode('string-escape'))

    def _init_from_raw(self):
        # TODO: retrieve mode from headers
        self._headers = self.raw_diff._headers

        # FIXME: workaround the mdiff path name
        match = re.match(r'^diff --git "?a\/(.+?)(?<!\\)"? "?b\/(.+?)(?<!\\)"?$',
                     self._headers[0])

        if match:
            self._old_path = match.group(1)
            self._new_path = match.group(2)
        else:
            self._old_path = re.sub(r"^\-\-\- (a\/)?", "",
                                   self.raw_diff._old_path).strip()
            self._new_path = re.sub(r"^\+\+\+ (b\/)?", "",
                                   self.raw_diff._new_path).strip()

        if self._old_path == "/dev/null":
            self.new_file = True
        if self._new_path == "/dev/null":
            self.deleted_file = True

        self.diff_with_lineno = list()
        self.diff = "".join(self._headers)
        self.diff += self.raw_diff._old_path
        self.diff += self.raw_diff._new_path

        self.diff = self.diff.encode('UTF-8')

        self.binary = False
        for header in self._headers:
            if header.startswith('Binary files'):
                self.binary = True
                break

        # retrieving hunk data, code snippet from
        # https://gist.github.com/aleiphoenix/6276707
        for hunk in self.raw_diff._hunks:

            self.diff += hunk._hunk_meta.encode('UTF-8')
            self.diff_with_lineno.append(('...', '...',
                                          hunk._hunk_meta.strip().encode('UTF-8'),
                                          'meta'))

            diff_start = False
            # cache changed line first
            old_lines = list()
            new_lines = list()

            for old, new, changed in hunk.mdiff():

                if changed:
                    diff_start = True
                    if not old[0]:
                        # new line
                        line = new[1].strip(b'\x00\x01')
                        if type(line) == unicode:
                            line = line.encode('UTF-8')
                        new_lineno = new[0] + hunk._new_addr[0] - 1
                        old_lineno = ""
                        new_lines.append((old_lineno, new_lineno,
                                         line, 'new'))
                    elif not new[0]:
                        # old line
                        line = old[1].strip(b'\x00\x01')
                        if type(line) == unicode:
                            line = line.encode('UTF-8')
                        new_lineno = ""
                        old_lineno = old[0] + hunk._old_addr[0] - 1
                        old_lines.append((old_lineno, new_lineno,
                                         line, 'delete'))
                    else:
                        line = b"-" + self._reset_control_chars(old[1])
                        if type(line) == unicode:
                            line = line.encode('UTF-8')
                        new_lineno = ""
                        old_lineno = old[0] + hunk._old_addr[0] - 1
                        old_lines.append((old_lineno, new_lineno,
                                         line, 'delete'))

                        line = b"+" + self._reset_control_chars(new[1])
                        if type(line) == unicode:
                            line = line.encode('UTF-8')
                        new_lineno = new[0] + hunk._new_addr[0] - 1
                        old_lineno = ""
                        new_lines.append((old_lineno, new_lineno,
                                         line, 'new'))

                else:
                    if diff_start:
                        self.diff += self._concat_lines(map(lambda x: x[2],
                                                            old_lines))
                        self.diff += self._concat_lines(map(lambda x: x[2],
                                                            new_lines))
                        self.diff_with_lineno.extend(old_lines)
                        self.diff_with_lineno.extend(new_lines)
                        old_lines = list()
                        new_lines = list()
                        diff_start = False
                    old_lineno = old[0] + hunk._old_addr[0] - 1
                    new_lineno = new[0] + hunk._new_addr[0] - 1
                    line = b" " + old[1]
                    if type(line) == unicode:
                        line = line.encode('UTF-8')
                    self.diff += line
                    self.diff_with_lineno.append((old_lineno, new_lineno,
                                                  line, 'match'))

            # when there is changed line only
            if diff_start:
                self.diff += self._concat_lines(map(lambda x: x[2], old_lines))
                self.diff += self._concat_lines(map(lambda x: x[2],
                                                    new_lines))
                self.diff_with_lineno.extend(old_lines)
                self.diff_with_lineno.extend(new_lines)
                diff_start = False

    def _concat_lines(self, lines):
        ret = b""
        for line in lines:
            if type(line) == unicode:
                line = line.encode('UTF-8')
            ret += line
        return ret

    def _reset_control_chars(self, line):
        line = line.replace(b'\x00-', b'')
        line = line.replace(b'\x00+', b'')
        line = line.replace(b'\x00^', b'')
        line = line.replace(b'\x01', b'')
        return line

    @staticmethod
    def list_from_string(raw_diff):
        """


        Args:
            raw_diff: is the utf-8 encoded diff raw string

        Returns:
            pygrit.diff.Diff[]
        """
        # TODO: maybe implement this from scratch ?
        if type(raw_diff) == unicode:
            raw_diff = raw_diff.encode('UTF-8')
        diff_hdl = StringIO(raw_diff)
        stream = PatchStream(diff_hdl)
        diffs = DiffParser(stream).get_diff_generator()

        result = list()
        for diff in diffs:
            result.append(Diff(diff))
        return result
