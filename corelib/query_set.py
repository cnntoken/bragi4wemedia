# -*- coding: utf-8 -*-

from mongoengine.queryset import QuerySet
from mongoengine.queryset.field_list import QueryFieldList

class LimitFetchingQuerySet(QuerySet):

    def __init__(self, document, collection):
        super(LimitFetchingQuerySet, self).__init__(document, collection)
        self._loaded_fields = QueryFieldList(fields=document._fields.iterkeys(), always_include=self._loaded_fields.always_include)
