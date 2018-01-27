"""bragi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url

from bragi import api_urls
from bragi import v1_urls
from accounts import urls as accounts_urls
from articles import urls as articles_urls
from comments import urls as comments_urls
from media import urls as media_urls
from statistics import urls as statistics_urls
from notifications import urls as notifications_urls
from admin import urls as admin_urls

from bragi import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^faq/$', views.faq),
    url(r'^api/sync_data/$', views.sync_data),
    url(r'^v1/', include(v1_urls)),
    url(r'^api/', include(api_urls)),
    url(r'^accounts/', include(accounts_urls)),
    url(r'^media/', include(media_urls)),
    url(r'^management/articles/', include(articles_urls)),
    url(r'^management/comments/', include(comments_urls)),
    url(r'^statistics/', include(statistics_urls)),
    url(r'^notifications/', include(notifications_urls)),
]
