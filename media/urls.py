# -*- coding: utf-8 -*-

from django.conf.urls import url
from media import views

urlpatterns = [
    url(r'^setup/$', views.setup),
    url(r'^incomes/$', views.incomes),
    url(r'^checkout/$', views.checkout),
    url(r'^checkout/account/$', views.checkout_account),
    url(r'^settings/$', views.settings),
    url(r'^incentive/$', views.incentive),
    url(r'^announcements/(?P<ann_id>[a-fA-F0-9]{24})/$', views.announcement_details)
]
