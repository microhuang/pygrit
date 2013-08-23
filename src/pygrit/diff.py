# -*- coding: utf-8 -*-
import re
from StringIO import StringIO

from cdiff import PatchStream, DiffParser



class Diff:

    serialize_keys = ["diff", "old_path", "new_path", "old_mode", "new_mode",
                      "new_file", "deleted_file", "renamed_file",
                      "diff_with_lineno"]

    def __init__(self, raw_diff):
        self.raw_diff = raw_diff

        self._headers = None

        sk = dict()
        for s in self.serialize_keys:
            sk[s] = None
        self.__dict__.update(sk)

        self._init_from_raw()

    def _init_from_raw(self):
        # TODO: retrieve mode from headers
        self._headers = self.raw_diff._headers

        self.old_path = re.sub(r"^\-\-\- (a\/)?", "",
                               self.raw_diff._old_path).strip()
        self.new_path = re.sub(r"^\+\+\+ (b\/)?", "",
                               self.raw_diff._new_path).strip()

        if self.old_path == "/dev/null":
            self.new_file = True
        if self.new_path == "/dev/null":
            self.deleted_file = True

        self.diff_with_lineno = list()
        self.diff = "".join(self._headers)
        self.diff += self.raw_diff._old_path
        self.diff += self.raw_diff._new_path

        # retrieving hunk data, code snippet from
        # https://gist.github.com/aleiphoenix/6276707
        for hunk in self.raw_diff._hunks:

            self.diff += hunk._hunk_meta
            self.diff_with_lineno.append(('...', '...',
                                          hunk._hunk_meta.strip(),
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
                        line = new[1].strip('\x00\x01')
                        new_lineno = new[0] + hunk._new_addr[0] - 1
                        old_lineno = ""
                        new_lines.append((old_lineno, new_lineno,
                                         line, 'new'))
                    elif not new[0]:
                        # old line
                        line = old[1].strip('\x00\x01')
                        new_lineno = ""
                        old_lineno = old[0] + hunk._old_addr[0] - 1
                        old_lines.append((old_lineno, new_lineno,
                                         line, 'delete'))
                    else:
                        line = "-" + self._reset_control_chars(old[1])
                        new_lineno = ""
                        old_lineno = old[0] + hunk._old_addr[0] - 1
                        old_lines.append((old_lineno, new_lineno,
                                         line, 'delete'))

                        line = "+" + self._reset_control_chars(new[1])
                        new_lineno = new[0] + hunk._new_addr[0] - 1
                        old_lineno = ""
                        new_lines.append((old_lineno, new_lineno,
                                         line, 'new'))

                else:
                    if diff_start:
                        self.diff += "".join(map(lambda x: x[2], old_lines))
                        self.diff += "".join(map(lambda x: x[2], new_lines))
                        self.diff_with_lineno.extend(old_lines)
                        self.diff_with_lineno.extend(new_lines)
                        old_lines = list()
                        new_lines = list()
                        diff_start = False
                    old_lineno = old[0] + hunk._old_addr[0] - 1
                    new_lineno = new[0] + hunk._new_addr[0] - 1
                    line = " " + old[1]
                    self.diff += line
                    self.diff_with_lineno.append((old_lineno, new_lineno,
                                                  line, 'match'))

            # when there is changed line only
            if diff_start:
                self.diff += "".join(map(lambda x: x[2], old_lines))
                self.diff += "".join(map(lambda x: x[2], new_lines))
                self.diff_with_lineno.extend(old_lines)
                self.diff_with_lineno.extend(new_lines)
                diff_start = False

    def _reset_control_chars(self, line):
        line = line.replace('\x00-', '')
        line = line.replace('\x00+', '')
        line = line.replace('\x00^', '')
        line = line.replace('\x01', '')
        return line
