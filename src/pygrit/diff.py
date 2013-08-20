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

            self.diff += "".join(hunk._hunk_headers)
            self.diff += hunk._hunk_meta

            diff_start = False
            old_lines = list()
            new_lines = list()

            for from_line, to_line, flag in hunk.mdiff():
                if flag:
                    diff_start = True
                    if from_line[0]:
                        old_line = from_line[1].lstrip("\0").rstrip("\1") \
                                                            .strip() + "\n"
                        old_lineno = from_line[0] + hunk._old_addr[0] - 1
                        new_lineno = ""
                        self.diff_with_lineno.append((old_lineno, new_lineno,
                                                      old_line.strip()))
                        old_lines.append(old_line)
                    if to_line[0]:
                        new_line = to_line[1].lstrip("\0").rstrip("\1") \
                                                          .strip() + "\n"
                        old_lineno = ""
                        new_lineno = to_line[0] + hunk._new_addr[0] - 1
                        self.diff_with_lineno.append((old_lineno, new_lineno,
                                                      new_line.strip()))
                        new_lines.append(new_line)
                else:
                    if diff_start:
                        self.diff += "".join(old_lines)
                        self.diff += "".join(new_lines)
                        diff_start = False
                    line = to_line[1].replace("\1", "").strip() + "\n"
                    old_lineno = from_line[0] + hunk._old_addr[0] - 1
                    new_lineno = to_line[0] + hunk._new_addr[0] - 1
                    self.diff_with_lineno.append((old_lineno, new_lineno,
                                                  line.strip()))
                    self.diff += " " + line

                if diff_start:
                    self.diff += "".join(old_lines)
                    self.diff += "".join(new_lines)
                    diff_start = False
