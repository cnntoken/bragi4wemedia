# -*- coding: utf-8 -*-

class Serializer(object):

    def __init__(self, query_set):
        self.query_set = query_set
        if not self.query_set:
            self._get_data = lambda: {}

    @property
    def data(self):
        return self._get_data()

    def _get_data(self):
        raise NotImplementedError
