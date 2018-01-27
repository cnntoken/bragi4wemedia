# -*- coding: utf-8 -*-

from corelib.serializers import Serializer
from corelib.time import datetime2india_timestr

class NotificationSerializer(Serializer):
    pass

class NSMixin(object):

    @property
    def published_time(self):
        return datetime2india_timestr(self.query_set.published_at)

class NotificationCompactSerializer(NSMixin, NotificationSerializer):

    def _get_data(self):
        info = dict(
            id=str(self.query_set.id),
            status=self.query_set.status,
            content=self.query_set.content,
            published_at=self.published_time,
            )
        return info

class NotificationDetailsSerializer(NotificationCompactSerializer):
    pass

