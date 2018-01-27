# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from statistics import utils as stat_utils

def articles_statistics(request):
    has_daily_data_synced = stat_utils.has_showing_data_synced()
    return render_to_response('article-analytics.html', locals())

def audience_statistics(request):
    return render_to_response('fans-analytics.html', locals())
