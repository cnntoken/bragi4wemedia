# -*- coding: utf-8 -*-
# NOTE: this string is magic! just like the lord of rings
#                                             :*=***====*:.
#                                        *==*****!*;;;;!*=:-::
#                                   *=@#$*!;;::--#!!!$;::*=#-:;=
#                                !@@@$*!;:::::*$#!!@!!=*=*$=!*,*!
#                             *@@@=!!;;::::;;!****!!;:-,,,-:-!-!!;
#                          *@@@=!!;;:::;;:::-:;-            !,-!!;$
#                       !*@$*;;;;;#$:---;;;                :;,;!!*$=
#                     *!=!;;::::=:::--;                   :!-:;!!*!!
#                   $!;;::-::;::::,-                     :!-;;;;:;!.
#                 $:::---:==-:--.                      !:;-;;;:-,@;.
#               =--:--!--!-,,.                        ;;:;;:;:-,*.-
#              *;-:--;:!:$,..                       :;;;;;::;:..
#             -,-----:--,.                        !;!;;;::;;:#-
#           =:.:,--,-..                         !;=!;;;:::;;*,
#          $:.-,:-,. . ;                      !=#=!;:;:::;*;.
#         =; -,-:;,.                        *#@$*!;:::::-:;,.
#         ;---::;::-                     *#@@#*!;;::;-=*,-; .
#        $- :,:-,,,.                  !$@@@#*!;;;;::#@,,.
#        $,:;:!*:;:               **@@@@@$=!!;;#:-;=--.
#        ==.:- *!!!           !=$@@@@#$=*!!!;;:@;;--,
#         *$*,:, .       ;=*#@@@@$=*!!!;;;;;#-::-,. ;
#          =$$=====***=$=$$$$*!!!;;;!::-:@;::-:-:-
#           $!=#$$$$===*!;;;:;!:;;!!;*--::::!!*
#             #==*=*;:--:::!**!!*!;;*:;!!*=:
#                @#@@$=@=#$*@=***;;:;!:
#                   !$$==**==**!:;
import operator

from bson.son import SON
from mongoengine import *
from mongoengine import signals
from mongoengine import ListField as _ListField, DictField as _DictField, SequenceField as _SequenceField
from mongoengine import Document as _Document
from mongoengine.common import _import_class
from bson.dbref import DBRef

from corelib.query_set import LimitFetchingQuerySet
from mongoengine import register_connection

class Document(_Document):
    meta = {'abstract': True, 'queryset_class': LimitFetchingQuerySet}

    def __init__(self, *args, **values):
        """
        Initialise a document or embedded document

        :param __auto_convert: Try and will cast python objects to Object types
        :param values: A dictionary of values for the document
        """
        self._initialised = False
        self._created = True
        if args:
            # Combine positional arguments with named arguments.
            # We only want named arguments.
            field = iter(self._fields_ordered)
            # If its an automatic id field then skip to the first defined field
            if getattr(self, '_auto_id_field', False):
                next(field)
            for value in args:
                name = next(field)
                if name in values:
                    raise TypeError(
                        "Multiple values for keyword argument '" + name + "'")
                values[name] = value

        __auto_convert = values.pop("__auto_convert", True)

        # 399: set default values only to fields loaded from DB
        __only_fields = set(values.pop("__only_fields", values))

        _created = values.pop("_created", True)

        signals.pre_init.send(self.__class__, document=self, values=values)

        # Check if there are undefined fields supplied to the constructor,
        # if so raise an Exception.
        if not self._dynamic and (self._meta.get('strict', True) or _created):
            _undefined_fields = set(values.keys()) - set(
                self._fields.keys() + ['id', 'pk', '_cls', '_text_score'])
            if _undefined_fields:
                msg = (
                    "The fields '{0}' do not exist on the document '{1}'"
                ).format(_undefined_fields, self._class_name)
                raise FieldDoesNotExist(msg)

        self._data = {}
        self._dynamic_fields = SON()

        # Assign default values to instance
        for key, field in self._fields.iteritems():
            if self._db_field_map.get(key, key) in __only_fields:
                continue
            value = getattr(self, key, None)
            setattr(self, key, value)

        if "_cls" not in values:
            self._cls = self._class_name

        # Set passed values after initialisation
        if self._dynamic:
            dynamic_data = {}
            for key, value in values.iteritems():
                if key in self._fields or key == '_id':
                    setattr(self, key, value)
                elif self._dynamic:
                    dynamic_data[key] = value
        else:
            FileField = _import_class('FileField')
            for key, value in values.iteritems():
                if key == '__auto_convert':
                    continue
                key = self._reverse_db_field_map.get(key, key)
                if key in self._fields or key in ('id', 'pk', '_cls'):
                    if __auto_convert and value is not None:
                        field = self._fields.get(key)
                        if field and not isinstance(field, FileField):
                            value = field.to_python(value)
                    setattr(self, key, value)
                else:
                    self._data[key] = value

        # Set any get_fieldname_display methods
        self.__set_field_display()

        if self._dynamic:
            self._dynamic_lock = False
            for key, value in dynamic_data.iteritems():
                setattr(self, key, value)

        # Flag initialised
        self._initialised = True
        self._created = _created
        signals.post_init.send(self.__class__, document=self)

    def __set_field_display(self):
        """Dynamically set the display value for a field with choices"""
        for attr_name, field in self._fields.items():
            if field.choices:
                if self._dynamic:
                    obj = self
                else:
                    obj = type(self)
                setattr(obj,
                        'get_%s_display' % attr_name,
                        partial(self.__get_field_display, field=field))

class ComplexBaseFieldMixin(object):

    def to_python(self, value):
        """Convert a MongoDB-compatible type to a Python type.
        """
        if isinstance(value, basestring):
            return value

        if hasattr(value, 'to_python'):
            return value.to_python()

        if not isinstance(value, (list, dict)):
            return value

        if isinstance(value, list):
            if self.field:
                return [self.field.to_python(item) for item in value]
            return [item.to_python() if hasattr(item, 'to_python') else self.to_python(item) for item in value]

        return dict((key, self.field.to_python(item)) for key, item in value.iteritems()) if self.field else \
                dict((k, v.to_python() if hasattr(v, 'to_python') else self.to_python(v)) for k, v in value.iteritems())

class ListField(ComplexBaseFieldMixin, _ListField):
    pass

class DictField(ComplexBaseFieldMixin, _DictField):
    pass

class SequenceField(_SequenceField):

    def __get__(self, instance, owner):
        """Descriptor for retrieving a value from a field in a document.
        """
        if instance is None:
            # Document class being used rather than a document object
            value = self
        else:
            # Get value from document instance if available
            value = instance._data.get(self.name)
        return value

    def to_python(self, value):
        return value


from bragi.settings import MONGODB_CONFIG, ASYNC_MQ_HOST, ASYNC_MQ_PORT, ASYNC_MQ_DB
from mongoengine.connection import DEFAULT_CONNECTION_NAME

def init_connection(config=MONGODB_CONFIG[DEFAULT_CONNECTION_NAME]):
    u'holy shit!'.encode('idna')
    connect(**config)
    register_connection('statistics', host=config['host'], port=config['port'], name='metrics')

def gen_reg_conf(conf):
    name = conf['db']
    host = conf['host']
    port = conf['port']
    return dict(name=name, host=host, port=port)

import redis
hot_conn = redis.Redis(host=ASYNC_MQ_HOST, port=ASYNC_MQ_PORT, db=ASYNC_MQ_DB)
