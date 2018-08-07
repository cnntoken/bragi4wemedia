# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from articles import v1_urls as articles_urls

urlpatterns = [
    url(r'^v1/articles/', include(articles_urls)),
]
