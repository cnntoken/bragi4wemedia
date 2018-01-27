# -*- coding: utf-8 -*-

from corelib.serializers import Serializer
from corelib.time import datetime2india_timestr, datetime2utc_timestr
from articles import processor as article_processor
from media import utils as media_utils
from statistics import utils as stat_utils


from gallery.models import Image
from gallery.serializers import GalleryImageSyncSerializer

class ArticleSerializer(Serializer):
    pass

class ArticleSerializerMixin(object):

    @property
    def published_time(self):
        return datetime2india_timestr(self.query_set.published_at)

    @property
    def last_modified_time(self):
        return datetime2india_timestr(self.query_set.last_modified_at)

    @property
    def checked_time(self):
        return datetime2india_timestr(self.query_set.checked_at)

    @property
    def submited_time(self):
        return datetime2india_timestr(self.query_set.submited_at)

    @property
    def takedown_time(self):
        return datetime2india_timestr(self.query_set.takedown_at)


class RealTimeStatisticsMixin(object):

    has_syncing_finished = True

    def get_stat_data(self):
        if not self.has_syncing_finished:
            return {
                    'show_count': None,
                    'read_count': None,
                    'comment_count': None,
                    'share_count': None,
                    'favorite_count': None,
                    }

        rec_count, read_count, share_count, comment_count, fav_count = \
                stat_utils.get_rt_article_showable_data(self.query_set)
        return {
                'show_count': rec_count,
                'read_count': read_count,
                'comment_count': comment_count,
                'share_count': share_count,
                'favorite_count': fav_count,
                }

    def real_time_statistics(self):
        pass

class RealTimeStatisticsGenerator(object):

    def __init__(self, articles, has_syncing_finished=True):
        if not has_syncing_finished:
            self.real_time_statistics_mapping = {
                    'show_count': None,
                    'read_count': None,
                    'comment_count': None,
                    'share_count': None,
                    'favorite_count': None,
                    }
            return

        if articles:
            articles_showable_data = stat_utils.get_rt_articles_showable_data(articles)
            self.real_time_statistics_mapping = articles_showable_data
        else:
            self.real_time_statistics_mapping = None

    def __call__(self, searilizer_item):
        if self.real_time_statistics_mapping is None:
            return searilizer_item
        statistics_mapping = lambda: self.real_time_statistics_mapping.get(str(searilizer_item.query_set.id), False)
        searilizer_item.real_time_statistics = statistics_mapping
        return searilizer_item

class AttachValidateInfoGenerator(object):

    def __init__(self, articles):
        language_articles_mapping = {}
        for article in articles:
            language = article.language
            if not language_articles_mapping.get(language):
                language_articles_mapping[language] = []
            language_articles_mapping[language].append(article)

        if articles:
            self.id_validate_info_mapping = {}
            from articles.utils import batch_check_validate_info
            for language in language_articles_mapping:
                articles = language_articles_mapping[language]
                validate_infos = batch_check_validate_info(articles, language)
                self.id_validate_info_mapping.update(validate_infos)
        else:
            self.id_validate_info_mapping = None

    def __call__(self, serializer_item):
        if self.id_validate_info_mapping is None:
            return serializer_item
        validate_info_mapping = lambda: self.id_validate_info_mapping.get(
                serializer_item.query_set.source_url, False)
        serializer_item.validate_info = validate_info_mapping
        return serializer_item

class StatisticsMixin(object):

    def get_stat_data(self):
        rec_count, read_count, share_count, comment_count, fav_count = \
                stat_utils.get_fixed_article_showable_data(self.query_set)
        return {
                'show_count': rec_count,
                'read_count': read_count,
                'comment_count': comment_count,
                'share_count': share_count,
                'favorite_count': fav_count,
                }

class ArticleDetailsSerializer(ArticleSerializerMixin, ArticleSerializer):

    def _get_data(self):
        info = dict(
            id=str(self.query_set.id),
            title=self.query_set.title,
            content=self.query_set.content,
            top_images=self.query_set.top_images,
            related_images=self.query_set.related_images,
            online_url=self.query_set.gen_online_url(),
            status=self.query_set.status,
            category=self.query_set.category,
            language=self.query_set.language,
            published_at=self.published_time,
            last_modified_at=self.last_modified_time,
            cover_type=self.query_set.cover_type,
            youtube_video_ids=self.query_set.youtube_video_ids,
            words_count=self.query_set.words_count,
            )
        return info

class ArticleSyncSerializer(ArticleSerializerMixin, ArticleSerializer):

    @property
    def published_time(self):
        return datetime2utc_timestr(self.query_set.published_at)

    @property
    def top_images(self):
        return self.deal_images(self.query_set.top_images)

    def deal_images(self, images):
        for image in images:
            for key in ['origin', 'thumb', 'headline']:
                if image.get(key):
                    self.join_jpg_image(image, key)
        return images

    def join_jpg_image(self, image, image_type):
        image_fragment = image[image_type].split('_')
        image_fragment.insert(1, 'jpg')
        image['%s_jpg'%image_type] = '_'.join(image_fragment)

    @property
    def related_images(self):
        return self.deal_images(self.query_set.related_images)

    def _get_data(self):
        info = dict(
            id=str(self.query_set.id),
            title=self.query_set.title,
            content=self.query_set.content,
            top_images=self.top_images,
            related_images=self.related_images,
            youtube_video_ids=self.query_set.youtube_video_ids,
            source_url=self.query_set.source_url,
            category=self.query_set.category,
            published_at=self.published_time,
            site_url=media_utils.gen_site_url(self.query_set.media_id),
            site_name=self.query_set.get_media().title,
            porn_score=4 if self.query_set.porn_score is None else self.query_set.porn_score,
            )
        return info

class ArticleCompactSerializer(ArticleSerializerMixin, ArticleSerializer):

    def _get_data(self):
        info = dict(
            id=str(self.query_set.id),
            title=self.query_set.title,
            category=self.query_set.category,
            top_images=self.query_set.top_images,
            online_url=self.query_set.gen_online_url(),
            status=self.query_set.status,
            language=self.query_set.language,
            published_at=self.published_time,
            last_modified_at=self.last_modified_time,
            checked_at=self.checked_time,
            submited_at=self.submited_time,
            takedown_at=self.takedown_time,
            check_reason=self.query_set.check_reason,
            check_reason_type=self.query_set.check_reason_type,
            words_count=self.query_set.words_count,
            )
        return info


class ArticleStatisticSerializer(RealTimeStatisticsMixin, ArticleCompactSerializer):

    def __init__(self, query_set, has_syncing_finished=True):
        self.query_set = query_set
        self.has_syncing_finished = has_syncing_finished

    def _get_data(self):
        info = super(ArticleStatisticSerializer, self)._get_data()
        info.update(self.real_time_statistics() or {})
        return info

class ArticleCompactStatisticSerializer(StatisticsMixin, ArticleSerializerMixin, ArticleSerializer):

    def _get_data(self):
        info = dict(
            id=str(self.query_set.id),
            title=self.query_set.title,
            online_url=self.query_set.gen_online_url(),
            status=self.query_set.status,
            language=self.query_set.language,
            published_at=self.published_time,
            words_count=self.query_set.words_count,
            )
        info.update(self.get_stat_data())
        return info

class AttachValidateInfoMixin(object):

    def gen_validate_info(self):
        from articles.utils import check_validate_info
        validate_info = check_validate_info(self.query_set)
        return {'validate_info': validate_info}

    def validate_info(self):
        pass

class ArticleAdminCompactSerializer(AttachValidateInfoMixin, RealTimeStatisticsMixin, ArticleCompactSerializer):

    def account_info(self):
        from media.models import MediaAccount
        ma = MediaAccount.objects.with_id(self.query_set.media_id)
        if not ma:
            return {}
        return {'title': ma.title, 'icon': ma.icon}

    def _get_data(self):
        data = super(ArticleAdminCompactSerializer, self)._get_data()
        data.update(dict(checker_email=self.query_set.checker_email,
                porn_score=4 if self.query_set.porn_score is None else self.query_set.porn_score))
        data.update({'validate_info': self.validate_info() or {}})
        data.update(self.real_time_statistics() or {})
        data.update({'media_account': self.account_info()})
        return data


class ArticleAdminDetailsSerializer(AttachValidateInfoMixin, RealTimeStatisticsMixin, ArticleDetailsSerializer):

    @property
    def checked_at(self):
        return datetime2india_timestr(self.query_set.checked_at)

    def _get_data(self):
        data = super(ArticleAdminDetailsSerializer, self)._get_data()
        data.update(dict(checker_email=self.query_set.checker_email,
            checked_at=self.checked_at,
            porn_score=4 if self.query_set.porn_score is None else self.query_set.porn_score))
        data.update(self.gen_validate_info())
        data.update(self.get_stat_data())
        return data
