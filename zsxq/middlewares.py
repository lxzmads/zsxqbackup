# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
from urllib.parse import urlsplit

from zsxq.api import ZsxqApi, ZsxqApiResponse


class ConvertToZsxqApiResponseMiddleware(object):
    """
    将来自api的Response转换为ZsxqApiResponse
    由于[1, 2]对response的class进行了分发，为了不受其影响，本middleware的顺序应小于590[2]

    References:
        [1] scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware
        [2] https://doc.scrapy.org/en/latest/topics/settings.html?highlight=settings#downloader-middlewares-base
        [3] https://github.com/scrapy/scrapy/issues/1877
    """

    def process_response(self, request, response, spider):
        if request.url.startswith(ZsxqApi.URL_API):
            return response.replace(cls=ZsxqApiResponse)
        return response


class AuthorizationMiddleware(object):
    """
    自动获取、添加、请求更新api授权相关变量的中间件
    通过selenium更新时，同样更新对应的User-Agent
    """

    # middleware是通过实例调用的
    # 为了维护全局的token/ua，需要放在类变量里
    TOKEN = None
    USER_AGENT = None

    @classmethod
    def from_crawler(cls, crawler):
        if crawler.settings['ZSXQ_ACCESS_TOKEN'] and crawler.settings['ZSXQ_USER_AGENT']:
            cls.TOKEN = crawler.settings['ZSXQ_ACCESS_TOKEN']
            cls.USER_AGENT = crawler.settings['ZSXQ_USER_AGENT']
        else:
            cls.TOKEN, cls.USER_AGENT = ZsxqApi.get_authorization()

        return cls()

    def process_request(self, request, spider):
        request.cookies[ZsxqApi.COOKIE_TOKEN_FIELD] = self.TOKEN
        request.headers['User-Agent'] = self.USER_AGENT

    def process_response(self, request, response, spider):
        if isinstance(response, ZsxqApiResponse) and response.code == 401:
            spider.logger.warn('access_token(%s)已失效: %r' % (self.TOKEN, response.body))
            AuthorizationMiddleware.TOKEN, AuthorizationMiddleware.USER_AGENT = ZsxqApi.get_authorization()
            return request
        return response

class HttpHostCheckMiddleware(object):
    """
    自动检测并修正request头部中host的中间件
    """

    def process_request(self, request, spider):
        url, host = request.url, request.headers.get('Host')
        real_host = urlsplit(url).netloc
        if not host or host != real_host:
            request.headers['Host'] = real_host

class ZSXQRetryMiddleware(object):
    def process_response(self, request, response, spider):
        if isinstance(response, ZsxqApiResponse) and response.code == 1059:
            retries = request.meta.get('retry_times', 0) + 1
            if(retries <= 7):
                spider.logger.warn("code is :" + str(response.code))
                retryreq = request.copy()
                retryreq.meta['retry_times'] = retries
                retryreq.dont_filter = True
                return retryreq
            else:
                spider.logger.error("retry max times")
                return response
        return response
