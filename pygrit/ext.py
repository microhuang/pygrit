# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import chardet


def encode(message):
    # FIXME: this unicode() ... just screwed python 2/3k compatibility (sign)
    if type(message) == unicode:
        return message
    else:
        result = chardet.detect(message)
        from pygrit import logger
        logger.debug(result)
        try:
            return message.decode(result['encoding'])
        except:
            return unicode(message, encoding='UTF-8', errors='replace')
