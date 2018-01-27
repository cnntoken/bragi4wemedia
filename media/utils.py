# -*- coding: utf-8 -*-

MP_SITE_URL_PREFIX = 'mp_'

def gen_site_url(media_id):
    return '%s%s' % (MP_SITE_URL_PREFIX, media_id)

def gen_media_id(site_url):
    return site_url.replace(MP_SITE_URL_PREFIX, '')
