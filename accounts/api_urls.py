# -*- coding: utf-8 -*-

from django.conf.urls import url
from accounts import api_views as views

urlpatterns = [
    url(r'^login/$', views.LoginView.as_view()),
]
