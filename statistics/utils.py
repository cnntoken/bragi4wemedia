# -*- coding: utf-8 -*-

from corelib.store import hot_conn
from itertools import groupby

STAT_TIMED_TASK_FINNISHED = 1
STAT_SYNC_SHOWING_FINISHED = 2

MP_FINISHED_KEY = 'mp_finished'

def has_timed_task_finished():
    data = hot_conn.get(MP_FINISHED_KEY)
    if not data:
        return False
    if not data.isdigit():
        return False
    stat = int(data)
    return stat == STAT_TIMED_TASK_FINNISHED

def set_showing_data_synced():
    hot_conn.set(MP_FINISHED_KEY, STAT_SYNC_SHOWING_FINISHED)

def has_showing_data_synced():
    data = hot_conn.get(MP_FINISHED_KEY)
    if not data:
        return False
    if not data.isdigit():
        return False
    stat = int(data)
    return stat == STAT_SYNC_SHOWING_FINISHED

def normalize_count(count):
    return count if count and count > 0 else 0

class DataValueNotUnique(Exception):
    def __str__(self):
        return self.__class__.__name__

def uniquify_data(counts):
    if not all(count == counts[0] for count in counts):
        raise DataValueNotUnique
    return counts[0] if counts else None

from mongoengine import context_managers
from media import utils as media_utils

def get_rt_media_showable_data(media_id):
    from articles.models import Article
    from statistics.models import (RealTimeMedia, DailyMedia, RealTimeArticle)
    from articles.consts import STATUS_PUBLISHED, STATUS_OFFLINE, STATUS_ADMIN_OFFLINE
    site_url = media_utils.gen_site_url(media_id)

    articles = Article.objects(media_id=str(media_id), status__in=[STATUS_PUBLISHED,
        STATUS_OFFLINE, STATUS_ADMIN_OFFLINE]).only('language', 'online_seq_id')
    articles = sorted((article for article in articles if article.online_seq_id), key=lambda x: x.language)
    rt_read_count = 0
    for lang, _articles in groupby(articles, lambda x: x.language):
        online_seq_ids = [article.online_seq_id for article in _articles]
        with context_managers.switch_db(RealTimeArticle, 'statistics') as RealTimeArticle:
            rt_stats = RealTimeArticle.objects(online_seq_id__in=online_seq_ids, lang=lang).only('read_count')
        rt_read_count += sum([normalize_count(stat.read_count) for stat in rt_stats])

    with context_managers.switch_db(RealTimeMedia, 'statistics') as RealTimeMedia:
        rt_medias = RealTimeMedia.objects(site_url=site_url)
    rt_follow_count = sum([normalize_count(rt_media.follow_count if rt_media else 0) \
            for rt_media in rt_medias])

    with context_managers.switch_db(DailyMedia, 'statistics') as DailyMedia:
        media_stats = DailyMedia.objects(site_url=site_url)
    follow_count = sum([normalize_count(stat.mp_fans_count) for stat in media_stats if stat.mp_fans_count])
    read_count = sum([normalize_count(stat.uclick_count) for stat in media_stats if stat.uclick_count])

    follow_count += rt_follow_count
    read_count += rt_read_count
    return follow_count, read_count

def get_fixed_media_read_count(media_id):
    site_url = media_utils.gen_site_url(media_id)
    from statistics.models import DailyMedia
    with context_managers.switch_db(DailyMedia, 'statistics') as DailyMedia:
        media_stats = DailyMedia.objects(site_url=site_url)
    read_count = sum([normalize_count(stat.uclick_count) for stat in media_stats if stat.uclick_count])
    return read_count

def get_fixed_article_showable_data(article):
    from statistics.models import DailyArticle
    rec_count = read_count = comment_count = share_count = fav_count = 0
    with context_managers.switch_db(DailyArticle, 'statistics') as DailyArticle:
        stats = DailyArticle.objects(online_seq_id=article.online_seq_id,
                lang=article.language)
    for stat in stats:
        rec_count += normalize_count(stat.rec_count)
        read_count += normalize_count(stat.uclick_count)
        share_count += normalize_count(stat.share_count)
        comment_count += normalize_count(stat.comment_count)
        fav_count += normalize_count(stat.favorite_count)
    return rec_count, read_count, share_count, comment_count, fav_count

def get_fixed_articles_showable_data(articles):
    online_seq_ids = []
    langs = []
    articles_mapping = {}
    for article in articles:
        if not article.online_seq_id:
            continue
        online_seq_ids.append(str(article.online_seq_id))
        langs.append(article.language)
        articles_mapping[str(article.online_seq_id)] = {'article_id': str(article.id), 'lang': str(article.language)}
    return get_fixed_articles_showable_data_for_dict(online_seq_ids, set(langs), articles_mapping)

def get_fixed_articles_showable_data_for_dict(online_seq_ids, langs, articles_mapping):
    from statistics.models import DailyArticle
    with context_managers.switch_db(DailyArticle, 'statistics') as DailyArticle:
        stats = DailyArticle.objects(online_seq_id__in=online_seq_ids,
                lang__in=langs)
    fixed_articles_showable_data = {}
    for stat in stats:
        if not articles_mapping[str(stat.online_seq_id)]['lang'] == stat.lang:
            continue
        key = articles_mapping[str(stat.online_seq_id)]['article_id']
        if not fixed_articles_showable_data.get(key):
            fixed_articles_showable_data[key] = {
                    'show_count': 0,
                    'read_count': 0,
                    'comment_count': 0,
                    'share_count': 0,
                    'favorite_count': 0
                }
        fixed_articles_showable_data[key]['show_count'] += normalize_count(stat.rec_count)
        fixed_articles_showable_data[key]['read_count'] += normalize_count(stat.uclick_count)
        fixed_articles_showable_data[key]['comment_count'] += normalize_count(stat.comment_count)
        fixed_articles_showable_data[key]['share_count'] += normalize_count(stat.share_count)
        fixed_articles_showable_data[key]['favorite_count'] += normalize_count(stat.favorite_count)
    return fixed_articles_showable_data

def get_rt_article_showable_data(article):
    from statistics.models import RealTimeArticle
    rec_count, read_count, share_count, comment_count, fav_count = \
            get_fixed_article_showable_data(article)

    with context_managers.switch_db(RealTimeArticle, 'statistics') as RealTimeArticle:
        rt_stat = RealTimeArticle.objects(online_seq_id=article.online_seq_id,
                lang=article.language).first()

    if rt_stat:
        rec_count += normalize_count(rt_stat.rec_count)
        read_count += normalize_count(rt_stat.read_count)
        comment_count += normalize_count(rt_stat.comment_count)
        share_count += normalize_count(rt_stat.share_count)
        fav_count += normalize_count(rt_stat.favorite_count)
    return rec_count, read_count, share_count, comment_count, fav_count

def get_media_fixed_article_read_reach_standard(media_id, standard):
    from articles.models import Article
    from statistics.models import DailyArticle
    articles = Article.objects(media_id=str(media_id))
    for article in articles:
        with context_managers.switch_db(DailyArticle, 'statistics') as DailyArticle:
            stats = DailyArticle.objects(online_seq_id=article.online_seq_id, lang=article.language)
        read_count = sum([normalize_count(stat.uclick_count) for stat in stats])
        if read_count >= standard:
            break
    else:
        return False
    return True

def get_rt_articles_showable_data(articles):
    online_seq_ids = []
    langs = []
    articles_mapping = {}
    for article in articles:
        if not article.online_seq_id:
            continue
        online_seq_ids.append(str(article.online_seq_id))
        langs.append(article.language)
        articles_mapping[str(article.online_seq_id)] = {'article_id': str(article.id), 'lang': str(article.language)}
    if not online_seq_ids:
        return None
    from statistics.models import RealTimeArticle
    articles_showable_data = get_fixed_articles_showable_data_for_dict(online_seq_ids, set(langs),
            articles_mapping)
    with context_managers.switch_db(RealTimeArticle, 'statistics') as RealTimeArticle:
        rt_stat = RealTimeArticle.objects(online_seq_id__in=online_seq_ids,
                lang__in=set(langs))

    for rt_stat_one in rt_stat:
        if not articles_mapping[str(rt_stat_one.online_seq_id)]['lang'] == rt_stat_one.lang:
            continue
        key = articles_mapping[str(rt_stat_one.online_seq_id)]['article_id']
        if not articles_showable_data.get(key):
            articles_showable_data[key] = {
                    'show_count': 0,
                    'read_count': 0,
                    'comment_count': 0,
                    'share_count': 0,
                    'favorite_count': 0
                }
        articles_showable_data[key]['show_count'] += normalize_count(rt_stat_one.rec_count)
        articles_showable_data[key]['read_count'] += normalize_count(rt_stat_one.read_count)
        articles_showable_data[key]['comment_count'] += normalize_count(rt_stat_one.comment_count)
        articles_showable_data[key]['share_count'] += normalize_count(rt_stat_one.share_count)
        articles_showable_data[key]['favorite_count'] += normalize_count(rt_stat_one.favorite_count)
    return articles_showable_data
