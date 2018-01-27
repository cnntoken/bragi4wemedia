# -*- coding: utf-8 -*-

from django.conf.urls import url
from comments import api_views as views

urlpatterns = [
    url(r'^$', views.CommentsView.as_view()),
    url(r'^article/(?P<article_id>[a-fA-F0-9]{24})/$', views.CommentsByArticleView.as_view()),
    url(r'^count/$', views.CommentsCountView.as_view()),
    url(r'^count/article/$', views.CommentsByArticleCountView.as_view()),
    url(r'^(?P<comment_id>[a-fA-F0-9]{24})/$', views.CommentDetailView.as_view()),
    url(r'^(?P<comment_id>[a-fA-F0-9]{24})/reply/$', views.CommentReplyDetailView.as_view()),
]
