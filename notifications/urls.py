# -*- coding: utf-8 -*-

from django.conf.urls import url
from notifications import views

urlpatterns = [
    url(r'^$', views.notification_list),
]
