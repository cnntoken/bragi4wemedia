# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse
from media import views as media_views

def anonymous_index(request):
    return render_to_response('login.html', locals())

def index(request):
    user = request.user
    if not request.user.is_anonymous():
        return media_views.management_index(request)
    return anonymous_index(request)


def faq(request):
    return render_to_response('faq.html',locals())

def sync_data(request):
    from statistics import utils as stat_utils
    stat_utils.set_showing_data_synced()
    return {'status': 'OK'}
