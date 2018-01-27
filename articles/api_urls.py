# -*- coding: utf-8 -*-

from django.conf.urls import url
from articles import api_views as views

urlpatterns = [
    url(r'^$', views.Articles.as_view()),
    url(r'^(?P<article_id>[a-fA-F0-9]{24})/$', views.ArticleDetails.as_view()),
    url(r'^(?P<article_id>[a-fA-F0-9]{24})/takedown/$', views.ArticleTakedown.as_view()),
    url(r'^(?P<article_status>submitted|offline|draft|published|failed|suspended)/', views.ArticlesWithStatus.as_view())
]
