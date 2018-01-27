# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from accounts import api_urls as accounts_urls
from articles import api_urls as articles_urls
from media import api_urls as media_urls
from gallery import api_urls as gallery_urls
from statistics import api_urls as statistics_urls
from comments import api_urls as comments_urls
from notifications import api_urls as notifications_urls
from admin import api_urls as admin_urls

urlpatterns = [
    url(r'^accounts/', include(accounts_urls)),
    url(r'^media/', include(media_urls)),
    url(r'^articles/', include(articles_urls)),
    url(r'^gallery/', include(gallery_urls)),
    url(r'^statistics/', include(statistics_urls)),
    url(r'^comments/', include(comments_urls)),
    url(r'^notifications/', include(notifications_urls)),
]
