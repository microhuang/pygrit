# -*- coding: utf-8 -*-

import os
import re
import subprocess
from glob import glob

from pygrit import logger

#
# class to interactive with `git` binary
#
class Git:

    # TODO: get from locale
    LOCALE_ENCODING = "UTF-8"

    ENCODING_PROCESS_NEEDED = ["author_name", "committer_name", "message"]

    def __init__(self, git_dir):
        self.git_dir = git_dir
        self.work_tree = re.sub(r"\/\.git$", "", git_dir)

    def get_commit(self, commit_id):
        """
        parse commit raw content to a dict
        """
        command = "git cat-file -p %s" % commit_id
        stdout, stderr = self._run_command(command, cwd=self.work_tree)

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

        stdout, stderr = self._run_command(command, cwd=self.work_tree)

        return stdout

    def refs(self, options, prefix):
        """
        return git refs list, line by line
        """
        refs = list()
        already = dict()
        os.chdir(self.git_dir)
        files = glob("%s/*" % prefix)
        for ref in files:
            if not os.path.isfile(ref):
                continue
            with open(ref) as f:
                id = f.read().strip()
            name = ref.replace(prefix + "/", "")
            if name not in already.keys():
                already[name] = True
                refs.append("%s %s" % (name, id))

        packed = "%s/%s" % (self.git_dir, 'packed-refs')
        if os.path.isfile(packed):
            with open(packed) as p:
                for line in p:
                    m = re.match(r'^(\w{40}) (.*?)$', line)
                    if m:
                        if not re.match(r'^' + prefix, m.group(2)):
                            continue
                        name = m.group(2).replace("%s/" % prefix, "")
                        if name not in already.keys():
                            already[name] = True
                            refs.append("%s %s" % (name, m.group(1)))
        return "\n".join(refs)

    def fs_mkdir(self, dir):
        command = "mkdir -p %s/%s" % (self.git_dir, dir)
        self._run_command(command, self.work_tree)

    def _process_encoding(self, result_dict):
        for k in self.ENCODING_PROCESS_NEEDED:
            result_dict[k] = result_dict[k].decode(self.LOCALE_ENCODING)
        return result_dict

    def _run_command(self, command, cwd):
        """
        TODO: try best to avoid running command thru shell
        """
        logger.debug(command)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=cwd)
        stdout, stderr = p.communicate()
        ret = p.returncode
        if ret != 0:
            raise OSError("git command cannot run: %s ; reason: %s" % \
                          (command, stderr))
        return stdout, stderr

    def _options_to_argv(self, options):
        argv = list()
        for o in options:
            if len(str(o)) == 1:
                # short option
                if type(options[o]) == bool and options[o]:
                    argv.append("-%s" % o)
                elif type(options[o]) == bool and options[o] == False:
                    # just ignore
                    pass
                else:
                    argv.append("-%s %s" % (o, options[o]))
            else:
                # long opton
                if type(options[o]) == bool and options[o]:
                    argv.append("--%s" % (str(o).replace("_", "-")) )
                elif type(options[o]) == bool and options[o] == False:
                    # just ignore
                    pass
                else:
                    argv.append("--%s=%s" % (str(o).replace("_", "-"),
                                             options[o]) )
        return argv

    def _native(self, cmd, *args, **options):
        """
        git binary call
        """
        # TODO: check security vunenrable problems
        opts = self._options_to_argv(options)
        args = " ".join(map(lambda x: str(x), args))
        command = "git %s %s %s" % (cmd.replace("_", "-"), " ".join(opts), args)

        stdout, stderr = self._run_command(command, self.work_tree)

        return stdout

    def __getattr__(self, name):
        """
        magic method missing call to native git binary
        """
        return lambda *args, **options: \
                               self._native(name, *args, **options)
