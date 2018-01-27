# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response

def notification_list(request):
    return render_to_response('notifications.html', locals())
