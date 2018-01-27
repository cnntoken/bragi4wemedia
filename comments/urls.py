# -*- coding: utf-8 -*-

from django.conf.urls import url
from comments import views

urlpatterns = [
    url(r'^$', views.comment_list),
    url(r'^(?P<article_id>[a-fA-F0-9]{24})/$', views.comment_detail),
]

