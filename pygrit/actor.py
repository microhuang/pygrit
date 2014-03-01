# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from pygrit.ext import encode

class Actor(object):

    def __init__(self, name, email=None):
        self._name = name
        self.email = email

    @property
    def name(self):
        return encode(self._name)

    def output(self, time):
        """Outpus an actor string for Git commits.

            actor = Actor('bob', 'bob@email.com')
            actor.output(time) # => "bob <bob@email.com> UNIX_TIME +0800"

        Args:
            +time The Time the commit was authored or committed

        Returns:
            a string
        """
        return "{} <{}> {} {}".format(self.name, self.email or "null",
                                      time.strftime("%s"), "0000")

    def __repr__(self):
        return '#<pygrit.Actor "{} <{}>">'.format(self.name, self.email)

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(string):
        if re.search(r'<.*>', string):
            from pygrit import logger
            logger.debug(string)
            m = re.match(r'(.*) <(.+?)>', string)
            if m:
                name = m.group(1)
                email = m.group(2)
                return Actor(name, email)
            else:
                return Actor('')
