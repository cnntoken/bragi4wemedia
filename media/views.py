# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from media.models import MediaPromotionUser

def verification_wating_page(request):
    return render_to_response('waiting.html', locals())

def verification_failed(request):
    return render_to_response('failed.html', locals())

def suspend(request):
    return render_to_response('suspend_account.html', locals())

def setup_page(request):
    return render_to_response('setup.html', locals())

def setup(request):
    u = request.user
    media_account = u.get_related_media_account()
    if not media_account:
        return setup_page(request)
    if media_account.verify_failed:
        return verification_failed(request)
    if media_account.verify_suspend:
        return suspend(request)

    return verification_wating_page(request)

def settings(request):
    return render_to_response('account-setting.html', locals())

def incentive(request):
    media = request.user.get_related_media_account()
    mpu = MediaPromotionUser.objects(media_id=str(media.id)).first()
    status = mpu.status
    return render_to_response('incentive.html', locals())

def management_index(request):
    return render_to_response('home.html', locals())

def announcement_details(request, ann_id):
    return render_to_response('announcement.html', locals())

def incomes(request):
    return render_to_response('income.html', locals())

def checkout(request):
    return render_to_response('checkout.html', locals())
def checkout_account(request):
    return render_to_response('account-info.html', locals())

