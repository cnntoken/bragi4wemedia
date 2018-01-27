# -*- coding: utf-8 -*-

from django.conf.urls import url
from accounts import views

urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
]
