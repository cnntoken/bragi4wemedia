# -*- coding: utf-8 -*-

from corelib.exception.processor import ExceptionProcessor

class ServerExceptionMiddleware(object):

    def process_exception(self, request, exception):
        processor = ExceptionProcessor(request, exception)
        return processor.get_response()
