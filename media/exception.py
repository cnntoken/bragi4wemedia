# -*- coding: utf-8 -*-

from corelib.exception.base import MBaseException

class MediaException(MBaseException):
    pass

class HasOwnMedia(MediaException):
    code = 40001

class InvalidMediaInfoUpdateFrequence(MediaException):
    code = 40002

class InvalidUpdateMediaField(MediaException):
    code = 40003

class MediaSyncFailed(MediaException):
    code = 40004

class MediaNameDuplicated(MediaException):
    code = 40005

class AnnouncementNotExist(MediaException):
    code = 40006

class MediaNotExist(MediaException):
    code = 40007

class MediaBankInfoNotExist(MediaException):
    code = 40008

class MediaPanNumRelatedTooMuch(MediaException):
    code = 40009

class MediaAccountReachSubmitLimit(MediaException):
    code = 40010

class MediaAccountWithDrawInProccessing(MediaException):
    code = 40011

class MediaAccountWithDrawNotInTime(MediaException):
    code = 40012

class MediaAccountInternshipSubmitLimit(MediaException):
    code = 40013

class MediaPanIsBlack(MediaException):
    code = 40014

class MediaPcodeNotExist(MediaException):
    code = 40015

class MediaPromotionCreateFail(MediaException):
    code = 40016

class MediaPcodeNotAllowable(MediaException):
    code = 40017

class MediaStatusNotAllowOperate(MediaException):
    code = 40018
