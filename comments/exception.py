# -*- coding:utf-8 -*-

from corelib.exception.base import MBaseException

class CommentsException(MBaseException):
    pass


class CommentsNotExists(MBaseException):
    code = 70001

class CommentsPageCountTooBig(MBaseException):
    code = 70002

class CommentsGetError(MBaseException):
    code = 70003

class CommentsReplyFail(MBaseException):
    code = 70004

class CommentsNoPrivilege(MBaseException):
    code = 70005
