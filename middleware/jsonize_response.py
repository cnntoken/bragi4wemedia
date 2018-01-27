# -*- coding: utf-8 -*-

from corelib.response import JsonResponse

class JsonizeResponseMiddleware(object):

    def process_response(self, request, response):
        url = request.get_full_path()
        if not (url.startswith('/api') or url.startswith('/v1')):
            return response

        if isinstance(response, (dict, list)):
            return JsonResponse(response)

        return response
