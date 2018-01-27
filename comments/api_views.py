# -*- coding: utf-8 -*-

from articles.models import Article
from articles.consts import STATUS_PUBLISHED

from corelib.requests import gen_page_query_params, gen_current_page_items
from corelib.exception.common import ParamError

from corelib.views import BaseView
from corelib.response import RESPONSE_OK, gen_page_response

from comments.models import Comment, CommentMediaInfo
from comments.consts import COMMENTS_PAGE_COUNT_MAX
from comments.exception import CommentsGetError, CommentsReplyFail, CommentsNoPrivilege
from comments import processor as comments_processor

from media.models import MediaAccount
from media.exception import MediaNotExist


class CommentsBaseView(BaseView):

    def dispatch(self, request, *args, **kwargs):
        response = super(CommentsBaseView, self).dispatch(request, *args, **kwargs)
        self.comment_media_info = CommentMediaInfo.objects(media_id=str(self.media_id)).first()
        if not self.comment_media_info:
            raise CommentsNoPrivilege
        return response

class CommentsView(CommentsBaseView):

    def get(self, request):
        count = request.GET.get('count', COMMENTS_PAGE_COUNT_MAX)
        site_url = self.media_account.site_url
        site_name = self.media_account.title
        sync_langs = self.media_account.lang_synced_status_mapping.keys()
        status, reason, comments = comments_processor.get_comments(site_url, site_name, count, sync_langs)
        if not status:
            raise CommentsGetError
        have_tag_langs = set()
        comment_media_info = CommentMediaInfo.objects(media_id=str(self.media_account.id)).first()
        for comment in comments:
            if comment['lang'] not in have_tag_langs:
                have_tag_langs.add(comment['lang'])
                if not comment_media_info.last_comment_tag_mapping.get(comment['lang']):
                    comment_media_info.last_comment_tag_mapping[comment['lang']] = ""
                if comment['id'] > comment_media_info.last_comment_tag_mapping[comment['lang']]:
                    comment_media_info.last_comment_tag_mapping[comment['lang']] = comment['id']
        comment_media_info.unread_comment_count = 0
        comment_media_info.save()
        return comments

    def post(self, request):
        data = request.DATA
        if not data:
            raise ParamError
        lang = data.get('lang')
        content = data.get('content')
        article_seq_id = data.get('article_seq_id')
        media_online_site_url = self.media_account.site_url
        reply_content = data.get('reply_content')
        reply_to = data.get('comment_id')
        reply_user = data.get('reply_user')
        reply_info = {'user': reply_user, 'id': reply_to, 'content': reply_content, 'article_seq_id': article_seq_id}
        status, reason, _ = comments_processor.reply_comment(lang, content, reply_info, media_online_site_url)
        if not status:
            raise CommentsReplyFail
        return RESPONSE_OK

class CommentDetailView(BaseView):

    def delete(self, request, comment_id):
        return {}

class CommentReplyDetailView(BaseView):

    def post(self, request, comment_id):
        return {}

class CommentsByArticleCountView(CommentsBaseView):

    def get(self, request):
        page_params, order, reverse, count = gen_page_query_params(request, 50)
        params = {'media_id': self.media_id, 'status': STATUS_PUBLISHED}
        params.update(page_params)
        articles, has_next_page = gen_current_page_items(Article, params, order, reverse, count)
        status, reason, comment_counts = comments_processor.get_comments_count_by_article(articles)
        if not status:
            raise CommentsGetError
        return gen_page_response(comment_counts, has_next_page)

class CommentsByArticleView(CommentsBaseView):

    def get(self, request, article_id):
        data = request.GET
        read_tag = data.get('read_tag', '')
        count = data.get('count', COMMENTS_PAGE_COUNT_MAX)
        action = data.get('action', 'next')
        article = Article.objects(id=article_id, status=STATUS_PUBLISHED).first()
        status, reason, data = comments_processor.get_comments_by_article(article, read_tag, int(count), action)
        if not status:
            raise CommentsGetError
        return gen_page_response(data['comments'], data['has_next_page'])

class CommentsCountView(CommentsBaseView):

    def get(self, request):
        comment_media_info = CommentMediaInfo.objects(media_id=str(self.media_account.id)).first()
        return {"unread_count": comment_media_info.unread_comment_count}
