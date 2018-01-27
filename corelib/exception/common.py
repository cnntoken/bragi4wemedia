# -*- coding: utf-8 -*-

from corelib.exception.base import MBaseException


class CommonException(MBaseException):
    pass

class NoPrivilege(CommonException):
    code = 10001

class ParamError(CommonException):
    code = 10002

class MediaAccountNotVerified(CommonException):
    code = 10003

class OwnNoAccount(CommonException):
    code = 10004

class NoAuthInfo(CommonException):
    code = 10005
