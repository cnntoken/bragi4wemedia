# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response

def create_article(request):
    return render_to_response('mob-post.html', locals())

def article_create_preview(request):
    return render_to_response('preview.html', locals())

def article_preview(request,article_id):
    return render_to_response('preview.html', locals())

def article_details(request,article_id):
    return render_to_response('mob-post.html', locals())

def article_list(request):
    return render_to_response('content-manage.html', locals())
