# -*- coding: utf-8 -*-

from corelib.exception.base import MBaseException

class NotificationException(MBaseException):
    pass

class NotificationNotExist(NotificationException):
    code = 60001
