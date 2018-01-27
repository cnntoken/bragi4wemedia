# -*- coding: utf-8 -*-

from django.http import Http404
from django.http.response import HttpResponse

from corelib.exception.base import MBaseException
from corelib.logging import log_exception, log2sentry

from bragi.settings import DEBUG

ERROR_CONTENT = '{"err_msg": "server error", "err_code": 1}'
ERROR_RESPONSE = HttpResponse(ERROR_CONTENT, status=500, content_type='application/json')


class ExceptionProcessor(object):

    def __init__(self, request, exception):
        self.request = request
        self.exception = exception

    def get_response(self):
        try:
            if isinstance(self.exception, Http404):
                return None

            if isinstance(self.exception, MBaseException):
                content = self.exception.get_response_content()
                status_code = self.exception.status_code
                response = HttpResponse(content, status=status_code, content_type='application/json')
                return response

            if DEBUG:
                return None

            req_data = self.request.GET
            req_data = req_data.dict()
            record = [str(req_data), self.request.body.replace('\n', ''), self.request.path]
            log_exception(record, request=self.request)

            return ERROR_RESPONSE
        except:
            log2sentry()
