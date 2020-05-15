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
REDIS_HOST = "45.151.175.204"
REDIS_PASSWORD = 99399
PATH = os.path.dirname(os.path.abspath(__file__))
GOOGLE_PATH = "operaxx1:/ig/20200514"


class RedisPoper:
    def __init__(self):
        self.r = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_PASSWORD, decode_responses=True)
        self.file_name = PATH + '/../data/' + str(int(round(time.time() * 1000))) + '.json'
        self.file = open(self.file_name, 'wb')
        self.file_size = 100
        self.max_nu = 10

    def poper(self):
        print(datetime.datetime.now(), "after 10s begin")
        time.sleep(10)
        key = "ig:items"
        nu = int(self.r.llen(key))
        if nu >= self.max_nu:
            fsize = round(os.path.getsize(self.file_name) / float(1024 * 1024))
            if fsize < self.file_size:
                for i in range(self.max_nu):
                    data = self.r.lpop(key)
                    line = data + "\n"
                    self.file.write(line.encode('utf-8'))
            else:
                self.file.close()
                self.file_name = PATH + '/../data/' + str(int(round(time.time() * 1000))) + '.json'
                self.file = open(self.file_name, 'wb')
                for i in range(self.max_nu):
                    data = self.r.lpop(key)
                    line = data + "\n"
                    self.file.write(line.encode('utf-8'))
            print(datetime.datetime.now(), "完成10个")
        time.sleep(10)


if __name__ == "__main__":
    rp = RedisPoper()
    while True:
        rp.poper()
