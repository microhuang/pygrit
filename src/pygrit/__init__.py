# -*- coding: utf-8 -*-

import logging
from logging import Formatter, StreamHandler
from sys import stdout

logger = logging.getLogger("pygrit")
handler = StreamHandler(stdout)
formatter = Formatter('[pygrit %(asctime)s %(levelname)-5s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
