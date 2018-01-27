# -*- coding: utf-8 -*-

from comments.models import CommentMediaInfo

from corelib.views import BaseView
from corelib.requests import gen_page_query_params, gen_current_page_items
from corelib.response import RESPONSE_OK, gen_page_response
from corelib.exception.common import NoPrivilege, ParamError

from notifications.models import Notification
from notifications.consts import (STATUS_UNREAD, STATUS_READ, NAME_STATUS_MAPPING,
        NOTIFICATION_ARTICLE_TYPES, NOTIFICATION_MEDIA_TYPES, NOTIFICATION_ADMIN_TYPES,
        NOTIFICATION_TYPE_MAPPING)
from notifications.serializers import (NotificationDetailsSerializer, NotificationCompactSerializer)
from notifications.exception import NotificationNotExist


class NotificationsBaseView(BaseView):

    def _get(self, request, article_status=None, type=None):
        params = {'media_id': self.media_id}
        if type is not None:
            params['type__in'] = NOTIFICATION_TYPE_MAPPING[type]
        if article_status:
            params['status'] = NAME_STATUS_MAPPING.get(article_status)
        page_params, order, reverse, count = gen_page_query_params(request)
        params.update(page_params)
        notifications, has_next_page = gen_current_page_items(Notification, params, order, reverse, count)
        return gen_page_response([NotificationCompactSerializer(notification).data \
                for notification in notifications], has_next_page)

class Notifications(NotificationsBaseView):

    def get(self, request):
        type = int(request.GET.get('type'))
        params = {'media_id': self.media_id}
        data = self._get(request, None, type=type)
        return data

    def delete(self, request):
        '''batch delete
        '''
        pass

class NotificationDetails(BaseView):

    def put(self, request, notification_id):
        notification = Notification.objects.with_id(notification_id)
        notification.update(set__status=STATUS_READ)
        return RESPONSE_OK

class NotificationsCount(BaseView):

    def get(self, request):
        notification_count = Notification.objects(media_id=self.media_id, status=STATUS_UNREAD).count()
        comment_media = CommentMediaInfo.objects(media_id=str(self.media_account.id)).first()
        if comment_media:
            comment_count = comment_media.unread_comment_count
        else:
            comment_count = 0
        return {
            'count': notification_count+comment_count, 'unread_comment_count': comment_count
            }

class NotificationTabCount(BaseView):

    def get(self, request):
        notification_article_count = Notification.objects(media_id=self.media_id, status=STATUS_UNREAD,
                type__in=NOTIFICATION_ARTICLE_TYPES).count()
        notification_media_count = Notification.objects(media_id=self.media_id, status=STATUS_UNREAD,
                type__in=NOTIFICATION_MEDIA_TYPES).count()
        notification_admin_count = Notification.objects(media_id=self.media_id, status=STATUS_UNREAD,
                type__in=NOTIFICATION_ADMIN_TYPES).count()
        return {
            'article_review_count': notification_article_count,
            'system_notification_count': notification_media_count,
            'admin_message_count': notification_admin_count,
            }
