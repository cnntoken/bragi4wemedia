# -*- coding: utf-8 -*-

from corelib.store import Document, StringField

class SyncHistory(Document):
    date = StringField()

    meta = {
        'indexes': [
            {
                'fields': ['date'],
                'unique': True,
            },
        ]
    }

    @classmethod
    def get_latest_sync_date(cls):
        sh = cls.objects.order_by('-id').first()
        if not sh:
            return None
        return sh.date
