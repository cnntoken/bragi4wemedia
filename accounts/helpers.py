# -*- coding: utf-8 -*-

def jump2media_page(user):
    media_account = user.get_related_media_account()
    if media_account and media_account.verify_passed:
        return '/'
    return '/media/setup/'
