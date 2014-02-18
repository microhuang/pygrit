# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from glob import glob
import os
import re
import subprocess
from tempfile import TemporaryFile
from time import sleep

from pygrit import logger
from pygrit.errors import GitTimeout
from pygrit.utils.wrappers import deprecated, should_in_git_python


#
# class to interactive with `git` binary
#
class Git:

    TIMEOUT  = 10
    INTERVAL = 0.1

    def __init__(self, git_dir):
        self.git_dir = git_dir
        self.work_tree = re.sub(r"\/\.git$", "", git_dir)

    @deprecated
    def get_diff(self, src, dst):

        if not dst:
            # TODO: compare current working dir
            raise NotImplementedError("cannot compare current working dir")

        command = "git diff %s %s" % (src, dst)

        stdout, stderr = self._run_command(command, cwd=self.work_tree)

        return stdout

    @should_in_git_python
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

    @should_in_git_python
    def rev_list(self, *refs, **options):
        if not refs:
            refs = ['master']
        if options.has_key('skip') and options['skip'] == 0:
            options.pop('skip')
        allowed_options = ['max_count', 'snice', 'until', 'pretty']
        if len(set(options.keys()) - set(allowed_options)) > 0 or len(refs) > 1:
            return self.__getattr__('rev-list')(*refs, **options)
        elif len(options) == 0:
            ref = refs[0]
            # "\n".join(file_index.commits_from(self.rev_parse(ref))) + "\n"
            return self.__getattr__('rev-list')(*refs, **options)
        else:
            ref = refs[0]
            aref = self.rev_parse(ref, verify=True)
            # if type(aref) == list:
            # TODO: implemented by git-python
            return self.__getattr__('rev-list')(*refs, **options)

    @should_in_git_python
    def rev_parse(self, string, **options):
        if type(string) not in (str, unicode):
            raise RuntimeError('invalid string %s' % string.__repr__())

        # Split ranges, but don't split when specifiying a ref:path.
        # Don't split HEAD:some/path/in/repo..txt
        # Do split sha1..sha2
        if not re.search(r':', string) and re.search(r'\.\.', string):
            sha1, sha2 = string.split("..")
            return [self.rev_parse({}, sha1), slef.rev_parse({}, sha2)]

        if re.match(r'^[0-9a-f]{40}$', string):
            return string.strip()

        head = "%s/refs/heads/%s" % (self.git_dir, string)
        if os.path.isfile(head):
            with open(head) as f:
                return f.read().strip()

        head = "%s/refs/remotes/%s" % (self.git_dir, string)
        if os.path.isfile(head):
            with open(head) as f:
                return f.read().strip()

        head = "%s/refs/tags/%s" % (self.git_dir, string)
        if os.path.isfile(head):
            with open(head) as f:
                return f.read().strip()

        # check packed-refs file, too
        packref = "%s/packed-refs" % self.git_dir
        if os.path.isfile(packref):
            with open(packref) as f:
                for line in f:
                    m = re.match(r'^(\w{40}) refs\/.+?\/(.*?)$', line)
                    if m:
                        if not re.match(re.escape(string) + "$", m.group(2)):
                            continue
                        return m.group(1).strip()

        # revert to calling git - grr
        return self.__getattr__('rev-parse')(string, **options).strip()

    def fs_mkdir(self, dir):
        command = "mkdir -p %s/%s" % (self.git_dir, dir)
        self._run_command(command, self.work_tree)

    def _run_command(self, command, cwd, raise_error=False):
        """
        TODO: try best to avoid running command thru shell
        """
        logger.debug('cwd: {}, command: {}'.format(cwd, command))
        stdout = TemporaryFile()
        stderr = TemporaryFile()
        p = subprocess.Popen(command, shell=True, stdout=stdout,
                             stderr=stderr, cwd=cwd)

        timeout = self.TIMEOUT
        interval = self.INTERVAL

        if timeout:
            slept = 0
            while True:
                if p.poll() is None:
                    if slept > timeout:
                        try:
                            p.kill()
                        except ProcessLookupError:
                            pass
                        raise GitTimeout("cwd: {}, command: {}"\
                                         .format(cwd, command))
                    sleep(interval)
                    slept += interval
                else:
                    break

        p.communicate()
        ret = p.returncode
        if ret != 0 and raise_error:
            raise OSError("git command cannot run: %s ; reason: %s" % \
                          (command, stderr))
        stdout.seek(0)
        stderr.seek(0)
        return stdout.read(), stderr.read()

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
        if options.has_key('raise_error'):
            raise_error = options.get('raise_error', False)
            options.pop('raise_error')

        opts = self._options_to_argv(options)
        args = " ".join(args)
        command = "git %s %s %s" % (cmd.replace("_", "-"), " ".join(opts), args)
        command = command.encode('UTF-8')

        stdout, stderr = self._run_command(command, self.work_tree)

        return stdout

    def __getattr__(self, name):
        """
        magic method missing call to native git binary
        """
        return lambda *args, **options: \
                               self._native(name, *args, **options)
