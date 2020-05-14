# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from tools.redis_login_info import RedisLoginInfo


class IgCrawlerSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class IgCrawlerDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return request

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


import time
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import json
import random
import InstagramAPI.InstagramAPI as IAPI
import requests
import urllib
import scrapy


def new_url(url, rank_token):
    query_string = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
    query_string["rank_token"] = rank_token
    new_url = url.split("?")[0]
    new_url += urllib.parse.urlencode(query_string)
    return new_url


class TooManyRequestsRetryMiddleware(RetryMiddleware):

    def __init__(self, crawler):
        super(TooManyRequestsRetryMiddleware, self).__init__(crawler.settings)
        self.crawler = crawler
        self.rli = RedisLoginInfo()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_response(self, request, response, spider):
        no_stop = self.rli.stop_crawler(self.crawler)
        if response.status == 200:
            self.rli.request_200_count()
        if response.status == 403 and no_stop:
            self.rli.request_403_count()
            # self.crawler.engine.pause()
            # self.crawler.engine.unpause()
            reason = response_status_message(response.status)
            user_info = self.rli.get_info()
            request.headers = user_info["headers"]
            request.cookies = user_info["cookies"]
            return self._retry(request, reason, spider) or response
        if response.status == 429:
            reason = response_status_message(response.status)
            self.rli.request_retry_count()
            user_info = self.rli.get_info()
            request.headers = user_info["headers"]
            request.cookies = user_info["cookies"]
            if "rank_token=max_id" in request.url:
                request.replace(url=request.url.replace("rank_token=max_id", "max_id"))
            return self._retry(request, reason, spider) or response
        elif response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            self.rli.request_retry_count()
            user_info = self.rli.get_info()
            request.headers = user_info["headers"]
            request.cookies = user_info["cookies"]
            if "rank_token=max_id" in request.url:
                request.replace(url=request.url.replace("rank_token=max_id", "max_id"))
            return self._retry(request, reason, spider) or response
        return response
