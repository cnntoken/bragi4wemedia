# -*- coding: utf-8 -*-

import datetime
from langdetect import detect_langs
from bs4 import BeautifulSoup

from corelib.views import BaseView
from django.views.generic import View
from corelib.requests import gen_article_page_query_params, gen_current_page_items
from corelib.response import RESPONSE_OK, gen_page_response
from corelib.consts import USABLE_LANGS
from corelib.exception.common import (ParamError, NoPrivilege, MediaAccountNotVerified)

from articles.models import Article
from articles.exception import (ArticleStatusCannotChanged, ArticleNotExist, ArticleSubmittedReachLimit,
        ArticleLanguageNotSupport, ArticleSyncFailed)
from articles.consts import (STATUS_DELETED, STATUS_DRAFT, STATUS_SUBMITTED, STATUS_PUBLISHED,
        STATUS_OFFLINE, STATUS_FAILED, USABLE_STATUSES, UNUSABLE_STATUSES, UPDATE_VALID_ACTIONS,
        NAME_STATUS_MAPPING)
from articles.serializers import ArticleStatisticSerializer, ArticleDetailsSerializer, RealTimeStatisticsGenerator
from articles import processor as article_processor
from statistics import utils as stat_utils
from media.exception import MediaAccountReachSubmitLimit, MediaAccountInternshipSubmitLimit
from media.models import PartnerToken

from admin.mixin import PassArticleMixin, AutoProcessMixin

def detect_lang(html_content, title):
    if html_content:
        soup = BeautifulSoup(html_content)
        text = soup.text
    else:
        text = ''
    title = title if title else ''
    languages = detect_langs('%s %s' % (text, title))
    if not languages:
        return 'en'
    for language in languages:
        if language.prob > 0.9:
            lang = language.lang
            if lang not in USABLE_LANGS:
                raise ArticleLanguageNotSupport
            return language.lang
    return 'en'

class ArticlesBaseView(BaseView):

    def _get(self, request, article_status=None):
        page_params, order, reverse, count = gen_article_page_query_params(request, 20)
        params = {'media_id': self.media_id}
        if article_status:
            params['status'] = NAME_STATUS_MAPPING.get(article_status)
        else:
            params['status__in'] = USABLE_STATUSES
        params.update(page_params)
        articles, has_next_page = gen_current_page_items(Article, params, order, reverse, count)
        has_syncing_finished = stat_utils.has_showing_data_synced()
        wrap_realtime = RealTimeStatisticsGenerator(articles, has_syncing_finished)
        return gen_page_response([wrap_realtime(ArticleStatisticSerializer(article, has_syncing_finished)).data \
                for article in articles], has_next_page)
'''
key: SITENAME_MD5
secret: SITEURL_MD5
'''
PARTNER_KEY_SECRET_MAPPING = {
        'cd0fbb7849b9b9d84c4f8e48e7301ecf': {
            'secret': '17fc83181ca4d0ed98e35796700c9903',
            'domain': 'www.outlookindia.com',
            }
}

class PartnerArticles(View):

    def post(self, request):
        partner_key = request.GET.get('partnerKey')
        partner_secret = request.GET.get('partnerSecret')
        token = PartnerToken.objects(partner_key=partner_key).first()
        if not token:
            raise NoPrivilege
        if not partner_secret == token.partner_secret:
            raise NoPrivilege
        domain = token.domain
        title = request.DATA.get('title')
        published_time = request.DATA.get('published_time')
        source_url = request.DATA.get('source_url')
        content = request.DATA.get('content')
        if None in (published_time, title, content, source_url):
            raise ParamError
        cover_images = request.DATA.get('cover_image', [])[:3]
        lang = detect_lang(content, title)
        status, reason, details = article_processor.create_partner_article(lang,
            source_url, domain, title, content, cover_images, published_time)
        if not status:
            raise ArticleSyncFailed
        return RESPONSE_OK


class Articles(AutoProcessMixin, PassArticleMixin, ArticlesBaseView):

    def post(self, request):
        data = request.DATA
        if not data:
            raise ParamError

        # NOTE: status in data
        status = data.get('status')
        if not status in UPDATE_VALID_ACTIONS:
            raise NoPrivilege

        now = datetime.datetime.utcnow()
        data['last_modified_at'] = now
        data['last_op_at'] = now
        if status == STATUS_DRAFT:
            article = Article.objects.create(media_id=str(self.media_account.id), **data)
            return {'id': str(article.id)}

        if not self.media_account.verify_passed:
            raise MediaAccountNotVerified

        if self.media_account.check_reached_submit_limit():
            raise MediaAccountReachSubmitLimit

        if self.media_account.check_internship_submit_limit():
            raise MediaAccountInternshipSubmitLimit

        lang = detect_lang(data.get('content'), data.get('title'))
        if lang:
            data['language'] = lang
        data['submited_at'] = now
        data['submit_times'] = 1
        article = Article.objects.create(media_id=str(self.media_account.id), **data)
        self.media_account.add_submit_log(str(article.id))
        self.auto_process_after_submitted(self.media_account, article)
        return {'id': str(article.id)}

    def get(self, request):
        return self._get(request, None)

    def delete(self, request):
        '''batch delete
        '''
        pass

class ArticlesWithStatus(ArticlesBaseView):

    def get(self, request, article_status):
        return self._get(request, article_status)


class ArticleDetails(AutoProcessMixin, PassArticleMixin, BaseView):

    def dispatch(self, request, article_id):
        self.article_id = article_id
        self.article = Article.objects.with_id(article_id)
        if not self.article:
            raise ArticleNotExist
        if self.article.status in UNUSABLE_STATUSES:
            raise ArticleNotExist
        response = super(ArticleDetails, self).dispatch(request)
        if not self.media_id == self.article.media_id:
            raise NoPrivilege
        return response

    def get(self, request):
        return ArticleDetailsSerializer(self.article).data

    def put(self, request):
        data = request.DATA
        if not data:
            raise ParamError

        if not self.article.status in (STATUS_DRAFT, STATUS_FAILED):
            raise ArticleStatusCannotChanged

        status = data.get('status')
        if not status in UPDATE_VALID_ACTIONS:
            raise NoPrivilege

        now = datetime.datetime.utcnow()

        has_modified = False
        for key, value in data.iteritems():
            if not key == 'status':
                has_modified = True
            setattr(self.article, key, value)

        if has_modified:
            self.article.last_modified_at = now
        self.article.last_op_at = now

        if status == STATUS_DRAFT:
            self.article.save()
            return RESPONSE_OK

        if self.media_account.check_reached_submit_limit():
            raise MediaAccountReachSubmitLimit
        if self.article.check_reached_submit_limit():
            raise ArticleSubmittedReachLimit
        if self.media_account.check_internship_submit_limit(str(self.article.id)):
            raise MediaAccountInternshipSubmitLimit
        self.article.submited_at = now
        if self.article.submit_times:
            self.article.submit_times = self.article.submit_times + 1
        else:
            self.article.submit_times = 1
        if 'content' in data or 'title' in data:
            lang = detect_lang(data.get('content', self.article.content), data.get('title', self.article.title))
            if lang:
                self.article.language = lang

        self.article.save()
        self.media_account.add_submit_log(str(self.article.id))
        self.auto_process_after_submitted(self.media_account, self.article)

        return RESPONSE_OK

    def delete(self, request):
        if not self.article.status in (STATUS_DRAFT, STATUS_FAILED):
            raise ArticleStatusCannotChanged
        now = datetime.datetime.utcnow()
        self.article.status = STATUS_DELETED
        self.article.deleted_at = now
        self.article.last_op_at = now
        self.article.save()
        return RESPONSE_OK

class ArticleTakedown(ArticleDetails):

    def post(self, request):
        if not self.article.status == STATUS_PUBLISHED:
            raise ArticleStatusCannotChanged
        now = datetime.datetime.utcnow()
        self.article.status = STATUS_OFFLINE
        self.article.takedown_at = now
        self.article.last_op_at = now
        self.article.save()
        article_processor.update_article_status(self.article.source_url, False, self.article.language)
        return RESPONSE_OK
