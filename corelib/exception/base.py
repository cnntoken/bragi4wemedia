# -*- coding: utf-8 -*-

import json

class MBaseException(Exception):
    code = None
    status_code = 400

    @property
    def msg(self):
        return self.__class__.__name__

    def __init__(self, *args, **kwargs):
        super(MBaseException, self).__init__(*args, **kwargs)

    def __str__(self):
        return 'Code: %s, Msg: %s' % (self.code, self.msg)

    def get_response_content(self):
        error_info = {'err_msg': self.msg, 'err_code': self.code}
        error_content = json.dumps(error_info)
        return error_content
