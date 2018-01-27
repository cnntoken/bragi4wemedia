# -*- coding: utf-8 -*-

from django.conf.urls import url
from statistics import views

urlpatterns = [
    url(r'^articles/$', views.articles_statistics),
    url(r'^audience/$', views.audience_statistics),
]
