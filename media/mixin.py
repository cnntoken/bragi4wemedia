# -*- coding: utf-8 -*-

from media.models import MediaAccount
from media.consts import UNFORMATTED_TITLE_BLACKLIST
from media.exception import MediaNameDuplicated

class CheckDuplicatedTitleMixin(object):

    def check_duplicated_title(self, title):
        unformatted_title = MediaAccount.gen_unformatted_title(title)
        if unformatted_title in UNFORMATTED_TITLE_BLACKLIST:
            raise MediaNameDuplicated
        media = MediaAccount.objects(unformatted_title=unformatted_title).first()
        if media:
            raise MediaNameDuplicated
        return unformatted_title
