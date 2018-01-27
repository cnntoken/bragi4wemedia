# -*- coding: utf-8 -*-

from django.conf.urls import url
from notifications import api_views as views

urlpatterns = [
    url(r'^$', views.Notifications.as_view()),
    url(r'^count/$', views.NotificationsCount.as_view()),
    url(r'^tab/count/$', views.NotificationTabCount.as_view()),
    url(r'^(?P<notification_id>[a-fA-F0-9]{24})/$', views.NotificationDetails.as_view()),
]
