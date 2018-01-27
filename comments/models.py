# -*- coding: utf-8 -*-

from corelib.store import (Document, StringField, DateTimeField, IntField, BooleanField, ListField, DictField)

class Comment(object):
    pass

class CommentMediaInfo(Document):
    media_id = StringField()
    media_title = StringField()
    sync_time = DateTimeField()
    unread_comment_count = IntField()
    usable = BooleanField()
    synced_langs = ListField(StringField())
    last_comment_tag_mapping = DictField()
