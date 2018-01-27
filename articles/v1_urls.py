# -*- coding: utf-8 -*-

from django.conf.urls import url
from articles import api_views as views

urlpatterns = [
    url(r'^$', views.PartnerArticles.as_view()),
]

