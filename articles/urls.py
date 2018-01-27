# -*- coding: utf-8 -*-

from django.conf.urls import url
from articles import views

urlpatterns = [
    url(r'^$', views.article_list),
    url(r'^create/$', views.create_article),
    url(r'^create/preview/$', views.article_create_preview),
    url(r'^(?P<article_id>[a-fA-F0-9]{24})/$', views.article_details),
    url(r'^(?P<article_id>[a-fA-F0-9]{24})/preview/$', views.article_preview),
]
