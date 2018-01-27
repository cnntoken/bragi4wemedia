# -*- coding: utf-8 -*-

from corelib.exception.base import MBaseException

class AccountException(MBaseException):
    pass

class UserNotExist(AccountException):
    code = 20001

class LoginRequired(AccountException):
    code = 20002
    status_code = 403

class HasLogin(AccountException):
    code = 20003

class EmailHasUsed(AccountException):
    code = 20004

class VerficationCodeUnusable(AccountException):
    code = 20005

class HasPassword(AccountException):
    code = 20006

class HasNoPassword(AccountException):
    code = 20007

class OldPasswordError(AccountException):
    code = 20008

class EmailNotExist(AccountException):
    code = 20009
