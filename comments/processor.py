# -*- coding:utf-8 -*-

import json
import thriftpy

from corelib.thrift_util import ThriftRequest
from bragi.settings import processor_prometheus_location_lang_mapping

from media import utils as media_utils

from comments.consts import COMMENTS_PAGE_COUNT_MAX
from comments.exception import CommentsPageCountTooBig

MP_COMMENT_THRIFT = thriftpy.load('comments/mp.thrift', module_name='comments_mp_thrift')

class MPCommentsRequestGenerator(ThriftRequest):
    processor_location_lang_mapping = processor_prometheus_location_lang_mapping
    thrift_cls = MP_COMMENT_THRIFT.MPCommentProcessService

comments_request_generator = MPCommentsRequestGenerator()

def ping(lang):
    return comments_request_generator.ping(lang)

def get_unread_comments_count(comment_media_infos):
    media_info_lang_mapping = {}
    for info in comment_media_infos:
        for lang in info.synced_langs:
            if not media_info_lang_mapping.get(lang):
                media_info_lang_mapping[lang] = []
            media_info_lang_mapping[lang].append(info)
    media_comments_counts_mapping = {}
    error_flag = False
    for lang in media_info_lang_mapping:
        comment_media_infos = media_info_lang_mapping[lang]
        media_infos = {media_utils.gen_site_url(info.media_id):info.last_comment_tag_mapping.get(lang) if info.last_comment_tag_mapping.get(lang) else '' for info in comment_media_infos}
        status, reason, data = comments_request_generator.wrap_func(lang, 'get_unread_comments_count', media_infos)
        if status:
            for key in data:
                if not media_comments_counts_mapping.get(key):
                    media_comments_counts_mapping[key] = 0
                media_comments_counts_mapping[key] += data[key]
        else:
            error_flag = True

    if error_flag and not media_comments_counts_mapping:
        return False, '', {}

    if error_flag:
        return True, 'some language maybe down', media_comments_counts_mapping

    return True, '', media_comments_counts_mapping

def get_comments(site_url, site_name, count, sync_langs):
    if count > COMMENTS_PAGE_COUNT_MAX:
        raise CommentsPageCountTooBig

    comments = []
    error_flag = False
    for lang in sync_langs:
        status, reason, data = comments_request_generator.wrap_func(lang, 'get_comments', site_url, site_name, count)
        if status:
            comments.extend(data)
        else:
            error_flag = True

    comments.sort(key=lambda scomment: scomment['id'], reverse=True)

    if error_flag and not comments:
        return False, '', []

    if error_flag:
        return True, 'some language maybe down', comments

    return True, '', comments

def reply_comment(lang, content, reply_info, media_online_site_url):
    return comments_request_generator.wrap_func(lang, 'reply_comment', *(int(reply_info['article_seq_id']), str(reply_info['user']['id']), content, json.dumps(reply_info['user']), reply_info['id'], reply_info['content'], media_online_site_url))

def get_comments_by_article(article_info, read_tag, count, action):
    lang = article_info.language
    seq_id = article_info.online_seq_id

    return comments_request_generator.wrap_func(lang, 'get_comments_by_article', seq_id, read_tag if read_tag else '', count, action)

def get_comments_count_by_article(article_infos):
    if len(article_infos) > COMMENTS_PAGE_COUNT_MAX:
        raise CommentsPageCountTooBig

    lang_articlce_seq_mapping = {}
    for info in article_infos:
        if not lang_articlce_seq_mapping.get(info.language):
            lang_articlce_seq_mapping[info.language] = {}
        lang_articlce_seq_mapping[info.language].update({str(info.online_seq_id): {'id':str(info.id), 'title': info.title}})

    comment_count_mapping = []
    error_flag = False
    for lang in lang_articlce_seq_mapping:
        article_seq_ids = lang_articlce_seq_mapping[lang].keys()
        status, reason, data = comments_request_generator.wrap_func(lang, 'get_comments_count_by_article', article_seq_ids)

        article_comment_count_mapping = [{'id': str(lang_articlce_seq_mapping[lang][one]['id']), 'title': lang_articlce_seq_mapping[lang][one]['title'], 'count':data[one]} for one in data]
        if status:
            comment_count_mapping.extend(article_comment_count_mapping)
        else:
            error_flag = True

    if error_flag and not comment_count_mapping:
        return False, '', []

    comment_count_mapping.sort(key=lambda scomment: scomment['id'], reverse=True)

    if error_flag:
        return True, 'some language is error', comment_count_mapping

    return True, '', comment_count_mapping
