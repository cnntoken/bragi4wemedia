# -*- coding: utf-8 -*-

from corelib.store import (Document, StringField, IntField, BooleanField)

class Image(Document):
    media_id = StringField()
    # image_type = StringField()
    width = IntField()
    height = IntField()
    origin = StringField()
    thumb = StringField()
    thumb_width = IntField()
    thumb_height = IntField()
    headline = StringField()
    headline_width = IntField()
    headline_height = IntField()
    usable = BooleanField()
    source = StringField()
    type = StringField()
    thumb_jpg = StringField()
    origin_jpg = StringField()
    headline_jpg = StringField()
