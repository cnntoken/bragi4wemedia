# -*- coding: utf-8 -*-

from django.contrib import auth
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response

import corelib.fb as facebook
from corelib.verification.models import VerificationCode
from accounts.models import User
from accounts.helpers import jump2media_page

def register(request):
    if not request.user.is_anonymous():
        return HttpResponseRedirect('/')
    return render_to_response('register.html', locals())

def login(request):
    if not request.user.is_anonymous():
        return HttpResponseRedirect('/')
    return render_to_response('login.html', locals())

def no_vcode_verification_page(request):
    return render_to_response('email_verification.html', locals())

def error_vcode_verification_page(request):
    return HttpResponse('render js verification page')

