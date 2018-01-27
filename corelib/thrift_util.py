# -*- coding:utf-8 -*-

import json
import thrift_connector.connection_pool as connection_pool

from corelib.logging import log2sentry

mp_processor_lang_mapping = {}

class ThriftRequest(object):
    processor_location_lang_mapping = []
    thrift_cls  = None

    def __init__(self):
        if not self.processor_location_lang_mapping:
            raise Exception("not set processor_location_lang_mapping")
        if not self.thrift_cls:
            raise Exception("not set thrift_cls")

    def get_proceesor_by_lang(self, lang):
        distincter = "%s-%s" % (self.thrift_cls.__name__, lang)
        processor = mp_processor_lang_mapping.get(distincter)
        if processor:
            return processor
        host, port = self.processor_location_lang_mapping[lang]
        processor = connection_pool.ClientPool(self.thrift_cls, \
            host, port, connection_class=connection_pool.ThriftPyCyClient)
        mp_processor_lang_mapping[distincter] = processor
        return processor

    def wrap_func(self, lang, func_name, *args):
        processor = self.get_proceesor_by_lang(lang)
        try:
            response = processor.__getattr__(func_name)(*args)
            if response.status:
                return response.status, response.reason, json.loads(response.data)
            return response.status, response.reason, {}
        except:
            log2sentry()
            return False, 'client error', {}

    def ping(self, lang):
        processor = self.get_proceesor_by_lang(lang)
        try:
            response = processor.ping()
            return response
        except:
            return "error"
