# -*- coding: utf-8 -*-

import os
import re
import subprocess

#
# class to interactive with `git` binary
#
class Git:

    # TODO: get from locale
    LOCALE_ENCODING = "UTF-8"

    ENCODING_PROCESS_NEEDED = ["author_name", "committer_name", "message"]

    def __init__(self, working_dir, default_branch='master'):
        if not os.path.exists(os.path.abspath(working_dir)):
            raise OSError("no such path")
        self.working_dir = working_dir

    def get_commit(self, commit_id):
        """
        parse commit raw content to a dict
        """
        command = "git cat-file -p %s" % commit_id
        stdout, stderr = self._run_command(command, cwd=self.working_dir)

        result = dict()
        result['id'] = commit_id
        result['parents'] = list()
        header, body = stdout.split("\n\n", 1)
        for line in header.split("\n"):
            if line.startswith("tree"):
                result['tree'] = line.split(" ")[1]
            if line.startswith("parent"):
                result['parents'].append(line.split(" ")[1])
            if line.startswith("author"):
                match = re.match(r'author\s'
                                 '(?P<author>.+)\s'
                                 '\<(?P<email>.+)\>\s'
                                 '(?P<timestamp>[0-9]+)\s'
                                 '(?P<offset>.+)', line)
                if match:
                    grp = match.groupdict()
                    result['author_name'] = grp['author']
                    result['author_email'] = grp['email']
                    result['authored_timestamp'] = grp['timestamp']
                    result['authored_offset'] = grp['offset']
            if line.startswith("committer"):
                match = re.match(r'committer\s'
                                 '(?P<committer>.+)\s'
                                 '\<(?P<email>.+)\>\s'
                                 '(?P<timestamp>[0-9]+)\s'
                                 '(?P<offset>.+)', line)
                if match:
                    grp = match.groupdict()
                    result['committer_name'] = grp['committer']
                    result['committer_email'] = grp['email']
                    result['committed_timestamp'] = grp['timestamp']
                    result['committed_offset'] = grp['offset']

            result['message'] = body

        result = self._process_encoding(result)
        return result

    def get_diff(self, src, dst):

        if not dst:
            # TODO: compare current working dir
            raise NotImplementedError("cannot compare current working dir")

        command = "git diff %s %s" % (src, dst)

        stdout, stderr = self._run_command(command, cwd=self.working_dir)

        return stdout

    def _process_encoding(self, result_dict):
        for k in self.ENCODING_PROCESS_NEEDED:
            result_dict[k] = result_dict[k].decode(self.LOCALE_ENCODING)
        return result_dict

    def _run_command(self, command, cwd):
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=cwd)
        stdout, stderr = p.communicate()
        ret = p.returncode
        if ret != 0:
            raise OSError("git command cannot run")
        return stdout, stderr
