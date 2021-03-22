# -*- coding: utf-8 -*-

# Scrapy settings for zsxq project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'zsxq'

SPIDER_MODULES = ['zsxq.spiders']
NEWSPIDER_MODULE = 'zsxq.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = ''

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Host': 'api.zsxq.com',
    'Origin': 'https://wx.zsxq.com',
    'Referer': 'https://wx.zsxq.com/dweb2/'
}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'zsxq.middlewares.AuthorizationMiddleware': 543,
    'zsxq.middlewares.ZSXQRetryMiddleware': 544,
    'zsxq.middlewares.ConvertToZsxqApiResponseMiddleware': 545,
    'zsxq.middlewares.HttpHostCheckMiddleware': 546,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'zsxq.pipelines.DuplicatesPipeline': 200,
    'zsxq.pipelines.ZsxqPipeline': 300,
    'zsxq.pipelines.GroupItemExportPipeline': 301,
    'zsxq.pipelines.TopicItemExportPipeline': 302,
    'zsxq.pipelines.TopicImagesPipeline': 303,
    'zsxq.pipelines.TopicFilesPipeline': 304,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Web Driver
CHROME_DRIVER_PATH = 'chromedriver'

BACKUP_MODE = 'white' # or black
# 备份的圈子id
PICK_GROUP_ID = [
    1337
]

# 不备份的圈子id
IGNORE_GROUP_ID = [
    758548854,  # 帮助与反馈
]

# 授权相关设置
ZSXQ_ACCESS_TOKEN = ''
ZSXQ_USER_AGENT = ''
