# -*- coding: utf-8 -*-
"""
实现了适应小密圈API特性的组件
"""

import json
import logging
from urllib.parse import urljoin, quote

from scrapy.http import TextResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import url_matches
from selenium.webdriver.support.wait import WebDriverWait

from zsxq.settings import CHROME_DRIVER_PATH
from zsxq.webdriver.expected_conditions import cookie_is_set, element_is_complete
from zsxq.webdriver.support import AutoClosableChrome

logger = logging.getLogger(__name__)


class ZsxqApi(object):
    """
    小密圈API接口信息
    """
    API_VERSION = 'v2'
    TEST_API = 'http://localhost:1337/'

    URL_API = 'https://api.zsxq.com/%s/' % API_VERSION
    # URL_API = TEST_API
    URL_LOGIN = 'https://wx.zsxq.com/dweb2/login'
    URL_GROUPS = urljoin(URL_API, 'groups')
    URL_TOPICS_FORMAT = urljoin(URL_API, 'groups/{group_id}/topics?scope=all&count=20&end_time={end_time}')

    URL_FILE_INFO_FORMAT = 'https://api.zsxq.com/%s/files/{file_id}' % API_VERSION
    URL_FILE_DOWNLOAD_FORMAT = '%s/%s' % (URL_FILE_INFO_FORMAT, 'download_url')

    # headers中access_token的字段名
    COOKIE_TOKEN_FIELD = 'zsxq_access_token'

    @staticmethod
    def URL_TOPICS(group_id, end_time=''):
        """
        话题数据API

        该API逻辑为，获取截止`end_time`时间最新的`count`条话题，
        并将最后一条话题的`create_time - 1ms`作为下次请求的`end_time`，
        为了避免对毫秒的处理，本项目直接使用`create_time`，并在返回结果中筛去。

        :param group_id: 圈子id
        :param end_time: 截止时间
        :return: 本次应请求的URL
        """
        return ZsxqApi.URL_TOPICS_FORMAT.format(group_id=group_id, end_time=quote(end_time))

    @staticmethod
    def URL_FILE_INFO(file_id):
        """
        文件信息API

        :param file_id: 文件id
        :return: URL
        """
        return ZsxqApi.URL_FILE_INFO_FORMAT.format(file_id=file_id)

    @staticmethod
    def URL_FILE_DOWNLOAD(file_id):
        """
        文件信息API

        :param file_id: 文件id
        :return: URL
        """
        return ZsxqApi.URL_FILE_DOWNLOAD_FORMAT.format(file_id=file_id)

    @staticmethod
    def get_authorization():
        """
        登录并获取授权相关信息
        :return: access_token, user-agent
        """

        with AutoClosableChrome(CHROME_DRIVER_PATH) as driver:
            driver.get(ZsxqApi.URL_LOGIN)

            # 获取User-Agent
            user_agent = driver.execute_script("return navigator.userAgent")

            # 等待跳转至主页
            WebDriverWait(driver, 60).until(url_matches(r'index/group/init'))
            logger.info('登录成功')

            # 等待access_token加载完毕
            access_token = WebDriverWait(driver, 30).until(cookie_is_set('zsxq_access_token'))
            access_token = access_token['value']

            # 等待头像加载完毕
            # 直接返回的token是不合法的，需要等待浏览器提交某请求使其合法，而该提交先于头像的加载
            # TODO: 似乎是加密了，有空再分析该请求
            # avatar_complete = element_is_complete((By.CSS_SELECTOR, 'p.avastar-p img'))
            # WebDriverWait(driver, 30).until(avatar_complete)
            

            logger.info('access_token加载成功: %s' % access_token)
            logger.info('user-agent加载成功: %s' % user_agent)
            # exit()
            return access_token, user_agent

    @staticmethod
    def get_image_url(image):
        """
        从data中获取尽可能清晰的图片url
        :param image: 图片数据
        :return: 图片url
        """
        for field in ['original', 'large', 'thumbnail']:
            if field in image:
                return image[field]['url']


class ZsxqApiResponse(TextResponse):
    """
    小密圈API的Response
    """

    def __init__(self, *args, **kwargs):
        super(ZsxqApiResponse, self).__init__(*args, **kwargs)
        if not self.url.startswith(ZsxqApi.URL_API):
            raise TypeError("不是来自API接口的请求: %s" % self.url)
        self.json = json.loads(self.text)

    @property
    def data(self):
        return self.json.get('resp_data')

    @property
    def success(self):
        return self.json.get('succeeded')

    @property
    def code(self):
        return self.json.get('code')