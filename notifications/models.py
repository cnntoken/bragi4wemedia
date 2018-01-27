# -*- coding: utf-8 -*-

import datetime

from corelib.store import Document, StringField, DateTimeField, IntField

from notifications.consts import STATUS_UNREAD

class Notification(Document):
    media_id = StringField()
    status = IntField()
    content = StringField()
    type = IntField()
    published_at = DateTimeField()


    @classmethod
    def create_notification(cls, media_id, n_type, content):
        now = datetime.datetime.utcnow()
        notification = cls.objects.create(status=STATUS_UNREAD, type=n_type,
                content=content, media_id=media_id, published_at=now)
        return notification
