#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import redis
import time
import os
import json
import datetime
from redis_login_info import RedisLoginInfo

# REDIS_HOST = "localhost"
REDIS_HOST = "45.11.0.16"
REDIS_PASSWORD = 99399
PATH = os.path.dirname(os.path.abspath(__file__))


class RedisPoper:
    def __init__(self):
        self.r = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_PASSWORD, decode_responses=True)

    def login_checker(self):
        rli = RedisLoginInfo()
        rli.check_403_count()
        rli.check_retry()
        time.sleep(30)


if __name__ == "__main__":
    rp = RedisPoper()
    while True:
        try:
            rp.login_checker()
        except:
            pass
