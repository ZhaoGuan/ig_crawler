#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import redis

# REDIS_HOST = "localhost"
# REDIS_HOST = "45.11.0.16"
REDIS_HOST = "45.151.175.204"
REDIS_PASSWORD = 99399


class RedisPusher:
    def __init__(self):
        self.r = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_PASSWORD, decode_responses=True)

    def push(self, url):
        self.r.rpush("ig", url)
