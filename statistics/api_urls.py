# -*- coding: utf-8 -*-

from django.conf.urls import url
from statistics import api_views as views

urlpatterns = [
    url(r'^total/$', views.StatisticsTotal.as_view()),
    url(r'^by_article/$', views.StatisticsByArticle.as_view()),
]
