# -*- coding: utf-8 -*-

import json
import thriftpy

from bragi.settings import processor_sol_location_lang_mapping
from corelib.thrift_util import ThriftRequest

article_processor_lang_mapping = {}

MP_ARTICLE_THRIFT = thriftpy.load('articles/mp.thrift', module_name='article_mp_thrift')

class MPArtcileRequestGenerator(ThriftRequest):
    processor_location_lang_mapping = processor_sol_location_lang_mapping
    thrift_cls = MP_ARTICLE_THRIFT.MPArticleProcessService

article_request_generator = MPArtcileRequestGenerator()

def check_usable_status(article_data, lang):
    article_json_data = json.dumps(article_data)
    return article_request_generator.wrap_func(lang, 'check_usable_status', *(article_json_data, lang,))

def batch_check_usable_status(articles_data, lang):
    articles_json_data = json.dumps(articles_data)
    return article_request_generator.wrap_func(lang, 'batch_check_usable_status', *(articles_json_data, lang))

def create_article(article_data, lang):
    article_json_data = json.dumps(article_data)
    return article_request_generator.wrap_func(lang, 'create_article', *(article_json_data,))

def create_partner_article(lang, source_url, domain, title, content, images, published_time):
    return article_request_generator.wrap_func(lang, 'create_partner_article', *(source_url, domain, title, content, images, published_time))

def update_article_status(source_url, usable, lang):
    return article_request_generator.wrap_func(lang, 'update_article_status', *(source_url, usable,))

def sync_media_account(media_data, lang):
    site_url = media_data['site_url']
    site_name = media_data['site_name']
    media_icon = media_data['media_icon']
    valid_duration = media_data['valid_duration']
    return article_request_generator.wrap_func(lang, 'sync_media_account', *(site_url, site_name, media_icon, valid_duration))

def article_insert_slot(article, lang):
    source_url = article.source_url
    return article_request_generator.wrap_func(lang, 'article_insert_slot', source_url)

