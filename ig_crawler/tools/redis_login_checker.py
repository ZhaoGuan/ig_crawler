#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import redis
import time
import os
import json
import datetime
from tools.redis_login_info import RedisLoginInfo
from tools.config import REDIS_HOST, REDIS_PASSWORD

PATH = os.path.dirname(os.path.abspath(__file__))


class RedisChecker:
    def __init__(self):
        self.r = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_PASSWORD, decode_responses=True)

    def login_checker(self):
        rli = RedisLoginInfo()
        rli.check_403_count()
        rli.check_retry()
        time.sleep(30)


