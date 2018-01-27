# -*- coding: utf-8 -*-

import json
from django.http.response import HttpResponse

class JsonResponse(HttpResponse):

    def __init__(self, content, *args, **kwargs):
        data = json.dumps(content)
        super(JsonResponse, self).__init__(data, content_type='application/json', *args, **kwargs)

RESPONSE_OK = {'status': 'OK'}

def gen_page_response(items, has_next_page):
    return dict(items=items, has_next_page=has_next_page)
