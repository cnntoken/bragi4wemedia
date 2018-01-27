# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from articles import v1_urls as articles_urls

urlpatterns = [
    url(r'^articles/', include(articles_urls)),
]
