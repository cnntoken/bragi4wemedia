# -*- coding: utf-8 -*-

from django.conf.urls import url
from gallery import api_views as views

urlpatterns = [
    url(r'^$', views.GalleryView.as_view()),
    url(r'^v1/by_url/$', views.GalleryByURLView.as_view()),
    url(r'^v1/capture/$', views.CaptureView.as_view()),
    url(r'^(?P<image_id>[a-fA-F0-9]{24})/$', views.ImageDetails.as_view()),
]
