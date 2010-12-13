# -*- coding: UTF-8 -*-

from __future__ import absolute_import
import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)
_log.addHandler(NullHandler())

from . import handler
from . import content
from . import structure
from . import prepared_statements
