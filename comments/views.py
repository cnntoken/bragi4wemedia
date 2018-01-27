# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response

def comment_list(request):
    return render_to_response('comments-manage.html', locals())


def comment_detail(request, article_id):
    return render_to_response('comments-detail.html', locals())
