# -*- coding: utf-8 -*-

import json
from urllib import quote
from django.http import HttpResponse, HttpResponseRedirect, Http404
from corelib.exception.common import NoPrivilege
from corelib.text_mapping.base import LANG_TEXT_MAPPING

NOT_LOGIN_RESPONSE = HttpResponse('{"err_code": 10005, "err_msg": "not usable user"}', status=403, content_type='application/json')

def gen_request_ip(request):
    if "HTTP_X_REAL_IP" in request.META:
        client_ip = request.META["HTTP_X_REAL_IP"]
    else:
        client_ip = request.META["REMOTE_ADDR"]
    return client_ip

class IdentityValidateMiddleware(object):
    NO_LOGIN_REQUIRE_URLS = {
        '/',
        '/faq/',
        '/v1/articles/'
    }

    ONLY_ANONYMOUS_URLS = {
        '/accounts/login/',
        '/accounts/register/',
        '/accounts/reset_password/',
        '/accounts/oauth/facebook/',
        '/accounts/oauth/facebook/callback/',
        '/api/accounts/login/',
        '/api/accounts/register/',
        '/api/accounts/reset_password/',
    }

    def process_request(self, request):
        url = request.path

        if url == '/api/sync_data/':
            return None

        # lang = request.COOKIES.get('lang','en')
        # NOTE: will have more lang
        lang = 'en'
        request.text_mapping = LANG_TEXT_MAPPING.get(lang, 'en')
        from bragi.settings import STATIC_VERSION
        request.static_version = STATIC_VERSION
        user = request.user
        request.csrf_processing_done = True
        from bragi.settings import LOGIN_URL
        if request.user.is_anonymous():
            if not (url in self.NO_LOGIN_REQUIRE_URLS or url in self.ONLY_ANONYMOUS_URLS):
                current_url = request.get_full_path()
                if current_url == '/accounts/logout/':
                    current_url = '/'
                return HttpResponseRedirect('%s?next=%s' % (LOGIN_URL, quote(current_url)))
            return None

        if url == '/accounts/logout/':
            return None

        if 'admin' in url:
            if request.user.is_staff:
                return None
            raise Http404

        if user.user_type == 'email' and not user.email_verified:
            if url == '/accounts/email_verification/':
                return None
            if url.startswith('/api'):
                return NOT_LOGIN_RESPONSE
            return HttpResponseRedirect('/accounts/email_verification/')

        if url in self.ONLY_ANONYMOUS_URLS:
            if url.startswith('/api'):
                return NOT_LOGIN_RESPONSE
            return HttpResponseRedirect('/')

        mid = request.GET.get('mid')
        if mid and user.is_superuser:
            media_account = user.get_related_media_account(god_view=True, mid=mid)
            request.mid = mid
            return None

        media_account = user.get_related_media_account()

        if media_account and media_account.verify_passed:
            if url == '/media/setup/':
                return HttpResponseRedirect('/')
            return None

        if url == '/':
            return HttpResponseRedirect('/media/setup/')

        if url == '/media/setup/':
            return None

        if not media_account:
            if url in ['/api/gallery/capture/', '/api/media/', '/api/media/check_info/']:
                return None

        if url.startswith('/api'):
            return NOT_LOGIN_RESPONSE
        return HttpResponseRedirect('/media/setup/')
