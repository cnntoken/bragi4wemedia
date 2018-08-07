# -*- coding: utf-8 -*-

from corelib.exception.base import MBaseException

class GalleryExcepiton(MBaseException):
    pass

class UploadFailed(GalleryExcepiton):
    code = 50001

class ImageNotExist(GalleryExcepiton):
    code = 50002

class ImageRenderFailed(GalleryExcepiton):
    code = 50003

