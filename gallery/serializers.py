# -*- coding: utf-8 -*-

from corelib.serializers import Serializer

class GallerySerializer(Serializer):
    pass

class GalleryImageSerializer(GallerySerializer):

    def _get_data(self):
        info = dict(
            id=str(self.query_set.id),
            width=self.query_set.width,
            height=self.query_set.height,
            origin=self.query_set.origin,
            thumb=self.query_set.thumb,
            thumb_width=self.query_set.thumb_width,
            thumb_height=self.query_set.thumb_height,
            headline=self.query_set.headline,
            headline_width=self.query_set.headline_width,
            headline_height=self.query_set.headline_height,
            type=self.query_set.type,
            )

        if self.query_set.thumb_jpg:
            info['thumb_jpg'] = self.query_set.thumb_jpg
        if self.query_set.origin_jpg:
            info['origin_jpg'] = self.query_set.origin_jpg
        if self.query_set.headline_jpg:
            info['headline_jpg'] = self.query_set.headline_jpg
        return info

class GalleryImageSyncSerializer(GalleryImageSerializer):

    def _get_data(self):
        info = super(GalleryImageSyncSerializer, self)._get_data()
        if self.query_set.thumb_jpg:
            info['thumb_jpg'] = self.query_set.thumb_jpg
        if self.query_set.origin_jpg:
            info['origin_jpg'] = self.query_set.origin_jpg
        if self.query_set.headline_jpg:
            info['headline_jpg'] = self.query_set.headline_jpg
