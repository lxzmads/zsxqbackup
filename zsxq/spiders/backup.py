# -*- coding: utf-8 -*-
import scrapy

from zsxq import settings
from zsxq.api import ZsxqApi
from zsxq.items import TopicImagesItem, TopicFilesItem, GroupItem, TopicItem


class BackupSpider(scrapy.Spider):
    name = 'backup'
    allowed_domains = ['zsxq.com']
    start_urls = [ZsxqApi.URL_GROUPS]

    def parse(self, response):
        for group in response.data['groups']:
            group_id = group['group_id']
            if(settings.BACKUP_MODE == 'black'):
                if group_id in settings.IGNORE_GROUP_ID:
                    continue
                yield GroupItem(_id=group_id, data=group)

                # 最新话题
                yield scrapy.Request(ZsxqApi.URL_TOPICS(group_id), callback=self.parse_topic)
            elif (settings.BACKUP_MODE == 'white'):
                if not group_id in settings.PICK_GROUP_ID:
                    continue
                yield GroupItem(_id=group_id, data=group)

                # 最新话题
                yield scrapy.Request(ZsxqApi.URL_TOPICS(group_id), callback=self.parse_topic)
            else:
                print("error mode")
                exit()

    def parse_topic(self, response):
        topics = response.data['topics']

        for topic in topics:
            topic_id, group_name = topic['topic_id'], topic['group']['name']
            yield TopicItem(_id=topic_id, data=topic, group_name=group_name)

            if topic['type'] == 'talk':

                # 图片
                images = topic['talk'].get('images')
                if images:
                    image_urls = map(ZsxqApi.get_image_url, images)
                    yield TopicImagesItem(_id=topic_id, data=images,
                                        group_name=group_name, image_urls=image_urls)

                # 文件
                files = topic['talk'].get('files')
                if files:
                    item = TopicFilesItem(_id=topic_id, data=files,
                                        group_name=group_name, file_urls=list())
                    url = ZsxqApi.URL_FILE_DOWNLOAD(files[0]['file_id'])
                    yield scrapy.Request(url, callback=self.parse_file, meta={'item': item, 'i': 1})

        # 下一批话题
        if topics:
            last_topic = topics[-1]
            url = ZsxqApi.URL_TOPICS(last_topic['group']['group_id'], last_topic['create_time'])
            print("last topic: "+last_topic['create_time'])
            yield scrapy.Request(url, callback=self.parse_topic)

    def parse_file(self, response):
        item, i = map(response.meta.get, ['item', 'i'])
        item['file_urls'].append(response.data['download_url'])
        if i < len(item['data']):
            url = ZsxqApi.URL_FILE_DOWNLOAD(item['data'][i]['file_id'])
            yield scrapy.Request(url, callback=self.parse_file, meta={'item': item, 'i': i + 1})
        else:
            yield item
