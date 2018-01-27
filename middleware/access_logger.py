# -*- coding: utf-8 -*-
import time

from corelib.logging import log_access, log2sentry
from corelib.requests import gen_request_ip

def _log_body(request):
    _body = getattr(request, '_body_', '')
    if 'password' in _body:
        return '******'
    content_type = request.META.get('CONTENT_TYPE')
    if not 'json' in content_type:
        return ''
    return _body[:50].decode('utf-8', 'ignore')

def _log_user(request):
    if request.user.is_anonymous():
        return ''
    if request.user.email:
        return request.user.email
    return str(request.user.id)

class LoggerMiddleware(object):

    def process_request(self, request):
        request.start_time = time.time()
        request._body_ = request.body

    def process_response(self, request, response):
        if response.status_code in {301, 302}:
            return response
        try:
            client_ip = gen_request_ip(request)
            start_time = getattr(request, 'start_time', time.time())
            proc_time = int((time.time() - start_time) * 1000)
            path = request.get_full_path()
            record = (request.method, path, _log_body(request), ' '.join(request.FILES.keys()),
                    client_ip, request.META.get('CONTENT_TYPE', ''), str(response.status_code),
                    request.META.get('HTTP_REFERER', ''), _log_user(request), str(proc_time))
            log_access(u'`'.join(record))
        except:
            log2sentry()
        return response
