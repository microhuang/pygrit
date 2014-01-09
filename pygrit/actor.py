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
        raise NotImplementedError()

    def __repr__(self):
        # cannot return unicode in repr function, WTF..
        return "#<pygrit.actor.Actor \"%s <%s>\">" %\
            (repr(self.name), self.email)

    @staticmethod
    def from_string(string):
        if re.search(r'<.*>', string):
            from pygrit import logger
            logger.debug(string)
            m = re.match(r'(.*) <(.*)>', string)
            if m:
                name = m.group(1)
                email = m.group(2)
                return Actor(name, email)
            else:
                return Actor('')
