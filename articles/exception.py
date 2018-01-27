# -*- coding: utf-8 -*-

from corelib.exception.base import MBaseException

class ArticleException(MBaseException):
    pass

class ArticleStatusCannotChanged(ArticleException):
    code = 30001

class ArticleNotExist(ArticleException):
    code = 30002

class ArticleSyncFailed(ArticleException):
    code = 30003

class ArticleSubmittedReachLimit(ArticleException):
    code = 30004

class ArticleStatusChangeNoAllowable(ArticleException):
    code = 30005

class ArticleLanguageNotSupport(ArticleException):
    code = 30006

class ArticleInsertSlotError(ArticleException):
    code = 30007

class ArticleSlotStatusError(ArticleException):
    code = 30008
