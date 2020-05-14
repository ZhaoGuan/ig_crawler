#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'


import json
import scrapy
import copy
from scrapy_redis.spiders import RedisSpider
import InstagramAPI.InstagramAPI as IAPI
import requests
import urllib
import random
from ig_crawler.items import IGItem
from scrapy.http import Request
from tools.redis_pusher import RedisPusher
from tools.redis_login_info import RedisLoginInfo


def to_json(response):
    return json.loads(response.body_as_unicode())

    '''
    429 请求过多问题 暂时的思路就是使用多个用户
    '''


class IG(RedisSpider):
    name = "ig"
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        # 'DOWNLOAD_DELAY': 8,
    }
    redis_key = 'ig'

    def __init__(self, *args, **kwargs):
        super(IG, self).__init__(*args, **kwargs)
        self.API_URL = 'https://i.instagram.com/api/v1/'
        self.SIG_KEY_VERSION = '4'
        self.pusher = RedisPusher()
        self.rli = RedisLoginInfo()
        # self.users = [
        # ["zhao.guan.wuren", "gz19891020"],
        # ["guanzhao001", "gz19891020"],
        # ["gz.fkz", "gz19891020"],
        # ["gz.fkz.000", "gz19891020"],
        # ]
        # for user in range(0, 130):
        #     try:
        #         self.login("cdc.cdc." + str(user), "gz19891020")
        #     except:
        #         print(str(user), "login fail")
        # for user in range(0, 100):
        #     try:
        #         self.login("cdc.cdc.cdc" + str(user), "gz19891020")
        #     except:
        #         print("cdc.cdc.cdc" + str(user), "login fail")
        # self.login("gz.fkz", "gz19891020")
        # self.login("cdc.cdc.25", "gz19891020")
        self.user_list = [
            "yuankeke001",
            "_charles_zhang",
            "knana129",
            "jinnii",
            "zhangmela",
            # "tsuziai",
            # "iiiigulee",
            "pmbian",
            "ter.zhao",
            # "velvet_cat",
            "japhethguo",
        ]
        self.user_list = [
            "kingjames",
            "kyliejenner",
            "nickiminaj",
            "kendalljenner",
            "iamcardib",
            "zendaya",
            "badgalriri",
            "billieeilish",
            "kevinhart4real",
            "selenagomez"
        ]

    '''lpush ig kingjames kyliejenner nickiminaj kendalljenner iamcardib zendaya badgalriri billieeilish kevinhart4real kevinhart4real selenagomez'''
    '''lpush ig velvet_cat yuankeke001 zhangmela tsuziai terzhao alina.archer'''

    def following_url(self, user_id, max_id=""):
        url = self.API_URL + 'friendships/' + str(user_id) + '/following/?'
        query_string = {'ig_sig_key_version': self.SIG_KEY_VERSION}
        if max_id:
            query_string['max_id'] = max_id
        url += urllib.parse.urlencode(query_string)
        return url

    def follower_url(self, user_id, max_id=""):
        if max_id == '':
            return self.API_URL + 'friendships/' + str(user_id) + '/followers/'
        else:
            return self.API_URL + 'friendships/' + str(
                user_id) + '/followers/?max_id=' + str(max_id)

    def make_requests_from_url(self, url):
        user_info = self.rli.get_info()
        url = self.API_URL + 'users/' + str(url) + '/usernameinfo/'
        return scrapy.Request(url=url, dont_filter=False, headers=user_info["headers"],
                              cookies=user_info["cookies"], callback=self.user_data,
                              meta={"level": 0})

    def user_data(self, response):
        user_info = self.rli.get_info()
        user_data = to_json(response)
        level = response.meta["level"]
        following_count = user_data["user"]["following_count"]
        follower_count = user_data["user"]["follower_count"]
        user_id = user_data["user"]["pk"]
        is_private = user_data["user"]["is_private"]
        if is_private is False:
            yield scrapy.Request(url=self.following_url(user_id), dont_filter=False,
                                 headers=user_info["headers"],
                                 cookies=user_info["cookies"], callback=self.following,
                                 meta={"user_data": user_data, "user_id": user_id, "following": [], "follower": [],
                                       "level": level, "follower_count": follower_count,
                                       "following_count": following_count})
        else:
            data = {"user_data": user_data, "following": [], "follower": [], "level": level}
            yield IGItem(data)

    def following(self, response):
        user_info = self.rli.get_info()
        meta = copy.copy(response.meta)
        user_id = meta["user_id"]
        user_data = meta["user_data"]
        following = meta["following"]
        follower = meta["follower"]
        following_count = meta["following_count"]
        follower_count = meta["follower_count"]
        level = meta["level"]
        json_data = to_json(response)
        try:
            next_max_id = json_data["next_max_id"]
        except:
            next_max_id = None
        user_list = []
        if next_max_id is not None:
            for user in json_data["users"]:
                following.append(user)
                user_list.append(user["username"])
                self.pusher.push(user["username"])
                yield scrapy.Request(url=self.following_url(user_id, next_max_id),
                                     dont_filter=False,
                                     headers=user_info["headers"], cookies=user_info["cookies"],
                                     callback=self.following,
                                     meta={"user_data": user_data, "user_id": user_id, "following": following,
                                           "follower": follower, "level": level, "follower_count": follower_count,
                                           "following_count": following_count})
            else:
                yield scrapy.Request(url=self.follower_url(user_id), dont_filter=False,
                                     headers=user_info["headers"],
                                     cookies=user_info["cookies"], callback=self.follower,
                                     meta={"user_data": user_data, "user_id": user_id, "following": following,
                                           "follower": follower, "level": level, "follower_count": follower_count,
                                           "following_count": following_count})

    def follower(self, response):
        user_info = self.rli.get_info()
        meta = copy.copy(response.meta)
        user_id = meta["user_id"]
        user_data = meta["user_data"]
        following = meta["following"]
        follower = meta["follower"]
        following_count = meta["following_count"]
        follower_count = meta["follower_count"]
        level = meta["level"]
        json_data = to_json(response)
        try:
            next_max_id = json_data["next_max_id"]
        except:
            next_max_id = None
        user_list = []
        for user in json_data["users"]:
            follower.append(user)
            user_list.append(user["username"])
            self.pusher.push(user["username"])
        if next_max_id is not None:
            yield scrapy.Request(url=self.follower_url(user_id, next_max_id), dont_filter=False,
                                 headers=user_info["headers"], cookies=user_info["cookies"], callback=self.follower,
                                 meta={"user_data": user_data, "user_id": user_id, "following": following,
                                       "follower": follower, "level": level, "follower_count": follower_count,
                                       "following_count": following_count})

        else:
            data = {
                "user_data": user_data,
                "following": following,
                "follower": follower,
                "level": level,
            }
            yield IGItem(data)
