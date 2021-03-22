# -*- coding: utf-8 -*-

import os
import time
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from collections import defaultdict

import scrapy
from scrapy import signals
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline

from zsxq.items import ZsxqItemExporter, GroupItem, TopicItem, TopicFilesItem, TopicImagesItem


class DuplicatesPipeline(object):
    """
    同一个spider下不同class的item分别去重

    References:
        [1] https://doc.scrapy.org/en/latest/topics/item-pipeline.html#duplicates-filter
    """

    def __init__(self):
        self.seen_ids = defaultdict(set)

    def process_item(self, item, spider):
        _class, _id = item.__class__, item['_id']
        if _id in self.seen_ids[_class]:
            raise DropItem('重复的 %s (%s)' % (_class, _id))
        self.seen_ids[_class].add(_id)
        return item


class BasePipeline(object):
    """
    基本的管道，包括绑定了信号的spider_opened和spider_closed两个方法
    """

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        pass

    def spider_closed(self, spider):
        pass


class ZsxqPipeline(BasePipeline):
    """
    项目pipeline，用于创建导出数据的目录
    """
    TIME_LABEL = time.strftime("%Y-%m-%d", time.localtime())
    EXPORT_PATH = os.path.join(os.getcwd(), 'downloads', TIME_LABEL)

    def spider_opened(self, spider):
        if not os.path.exists(self.EXPORT_PATH):
            os.makedirs(self.EXPORT_PATH)


class GroupItemExportPipeline(BasePipeline):
    """
    处理Group的pipeline
    """
    EXPORT_PATH = os.path.join(ZsxqPipeline.EXPORT_PATH, 'groups.json')

    def spider_opened(self, spider):
        self.file = open(self.EXPORT_PATH, 'wb')
        self.exporter = ZsxqItemExporter(self.file)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        if type(item) is GroupItem:
            self.exporter.export_item(item)
        return item


class TopicItemExportPipeline(BasePipeline):
    """
    处理Topic的pipeline

    每个group下的topics分别存储在不同的json文件中
    """
    EXPORT_PATH = os.path.join(ZsxqPipeline.EXPORT_PATH, '{name}')

    def __init__(self):
        self.files, self.exporters = {}, {}
        self.seen_groups = set()

    def spider_closed(self, spider):
        list(map(lambda e: e.finish_exporting(), self.exporters.values()))
        list(map(lambda f: f.close(), self.files.values()))

    def process_item(self, item, spider):
        if type(item) is TopicItem:
            name = self.__check_group(item['group_name'])
            self.exporters[name].export_item(item)
        return item

    def __check_group(self, name):
        if name not in self.seen_groups:
            self.seen_groups.add(name)

            path = self.EXPORT_PATH.format(name=name)
            os.makedirs(path)

            file = open(os.path.join(path, 'topics.json'), 'wb')
            self.files[name] = file

            exporter = ZsxqItemExporter(file)
            exporter.start_exporting()
            self.exporters[name] = exporter
        return name


class TopicImagesPipeline(ImagesPipeline):
    """
    下载TopicImages的pipeline

    以image_id为文件名，按group_name分组存储在images目录下
    """

    @classmethod
    def from_settings(cls, settings):
        return cls(ZsxqPipeline.EXPORT_PATH, settings=settings)

    def get_media_requests(self, item, info):
        for url, image in zip(item['image_urls'], item['data']):
            yield scrapy.Request(url, meta={'path': self._make_path(item, image)})

    def process_item(self, item, spider):
        if not type(item) is TopicImagesItem:
            return item
        return super(TopicImagesPipeline, self).process_item(item, spider)

    def file_path(self, request, response=None, info=None):
        return request.meta['path']

    def _make_path(self, item, image):
        return '{}/images/{}.jpg'.format(item['group_name'], image['image_id'])


class TopicFilesPipeline(FilesPipeline):
    """
    下载TopicFile的pipeline

    按group_name分组存储在files目录下
    """

    @classmethod
    def from_settings(cls, settings):
        return cls(ZsxqPipeline.EXPORT_PATH, settings=settings)

    def get_media_requests(self, item, info):
        for url, file in zip(item['file_urls'], item['data']):
            yield scrapy.Request(url, meta={'path': self._make_path(item, file)})

    def process_item(self, item, spider):
        if not type(item) is TopicFilesItem:
            return item
        return super(TopicFilesPipeline, self).process_item(item, spider)

    def file_path(self, request, response=None, info=None):
        return request.meta['path']

    def _make_path(self, item, file):
        return '{}/files/{}'.format(item['group_name'], file['name'])
