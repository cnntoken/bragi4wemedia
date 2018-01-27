# -*- coding: utf-8 -*-

from django.http import Http404
from django.views.generic import View

from corelib.exception.common import MediaAccountNotVerified, OwnNoAccount

class BaseView(View):

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        mid = request.GET.get('mid')
        if mid and user.is_superuser:
            request.mid = mid
            media_account = user.get_related_media_account(god_view=True, mid=mid)
        else:
            media_account = user.get_related_media_account()
        if not media_account:
            raise OwnNoAccount
        self.media_account = media_account
        if not self.media_account.verify_passed:
            raise MediaAccountNotVerified
        self.media_id = str(self.media_account.id)
        return super(BaseView, self).dispatch(request, *args, **kwargs)

class AdminBaseView(View):

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            raise Http404
        return super(AdminBaseView, self).dispatch(request, *args, **kwargs)

