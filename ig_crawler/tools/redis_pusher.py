#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import redis
from .config import REDIS_HOST, REDIS_PASSWORD


class RedisPusher:
    def __init__(self):
        self.r = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_PASSWORD, decode_responses=True)

    def push(self, url):
        self.r.rpush("ig", url)
