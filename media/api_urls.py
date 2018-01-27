# -*- coding: utf-8 -*-

from django.conf.urls import url
from media import api_views as views

urlpatterns = [
    url(r'^$', views.MediaView.as_view()),
    url(r'^check_info/$', views.MediaCheckInfoView.as_view()),
    url(r'^settings/$', views.MediaSettings.as_view()),
    url(r'^settings/payment_info/$', views.MediaPaymentInfo.as_view()),
    url(r'^withdraws/$', views.MediaWithDraw.as_view()),
    url(r'^bonus/$', views.MediaBonus.as_view()),
    url(r'^incomes/$', views.MediaIncomes.as_view()),
    url(r'^withdraws/stat/$', views.MediaWithDrawStat.as_view()),
    url(r'^statistics/base/$', views.MediaStatisticsView.as_view()),
    url(r'^announcements/$', views.PlatformAnnouncement.as_view()),
    url(r'^announcements/(?P<ann_id>[a-fA-F0-9]{24})/$', views.AnnouncementDetailsView.as_view()),
    url(r'^promotion/$', views.PromotionView.as_view()),
    url(r'^promotion_log/$', views.PromotionLogView.as_view()),
]

