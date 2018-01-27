# -*- coding: utf-8 -*-

import json

class RESTfulRequestMiddleware(object):

    def gen_json_data(self, request):
        if not request.body:
            return {}
        try:
            data = json.loads(request.body)
        except:
            return {}
        return {} if not data else data

    def process_request(self, request):
        method = request.method
        if method == 'POST':
            request.method = method
            data = self.gen_json_data(request)
            setattr(request, 'DATA', data)
        elif method in ('PUT', 'DELETE'):
            request.method = 'POST'
            request._load_post_and_files()
            data = self.gen_json_data(request)
            request.method = method
            setattr(request, 'DATA', data)
