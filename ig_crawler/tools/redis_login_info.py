#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import redis
import time
import os
import json
import datetime

import InstagramAPI.InstagramAPI as IAPI
import requests
import random
import threadpool

# REDIS_HOST = "localhost"
REDIS_HOST = "45.11.0.16"
REDIS_PASSWORD = 99399
PATH = os.path.dirname(os.path.abspath(__file__))
login_data_path = PATH + "/../login_data.json"
user_info_path = PATH + "/../user_info.txt"


class IGLogin():
    def __init__(self):
        self.login_result = []
        self.err_400_file_name = "./error/" + str(int(round(time.time() * 1000))) + "_400.txt"
        self.err_429_file_name = "./error/" + str(int(round(time.time() * 1000))) + "_429.txt"

    def login(self, case, count=0):
        user = case[0]
        password = case[1]
        api = IAPI(user, password)
        if api.login():
            print("login pass!!!")
            print(user)
            self.login_result.append(
                {"headers": dict(api.s.headers), "cookies": requests.utils.dict_from_cookiejar(api.s.cookies),
                 "rank_token": api.rank_token})
        else:
            if api.LastResponse.status_code == 429:
                count += 1
                if count < 10:
                    print("login fail!!!")
                    print(user)
                    print("error 429")
                    time.sleep(60)
                    self.login(case, count)
                    with open(self.err_429_file_name, "a+") as f:
                        f.write(user + "," + password + ",400\n")
            if api.LastResponse.status_code == 400:
                print("login fail!!!")
                print(user)
                print("error 400")
                with open(self.err_400_file_name, "a+") as f:
                    f.write(user + "," + password + ",400\n")
        print(len(self.login_result))

    def m_login(self, cases):
        pool = threadpool.ThreadPool(20)
        pool_requests = threadpool.makeRequests(self.login, cases)
        [pool.putRequest(req) for req in pool_requests]
        pool.wait()

    def re_login(self):
        cases = []
        with open(user_info_path, "r") as user_info:
            for user in user_info.readlines():
                try:
                    user_name = user.split(",")[0]
                    password = user.split(",")[1].replace("\n", "")
                    cases.append([user_name, password])
                    self.login([user_name, password])
                except:
                    pass
        # self.m_login(cases)
        with open(login_data_path, "w") as f:
            print("login success count:")
            print(len(self.login_result))
            data = {'data': self.login_result}
            json.dump(data, f)
        self.login_result = []


class RedisLoginInfo:
    def __init__(self):
        self.r = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_PASSWORD, decode_responses=True)
        self.login_data_path = login_data_path
        self.key_name = "login"
        self.rrc_key = "rrc"
        self.f_t_o = "403"
        self.rrc_max = 20000
        self.f_t_o_max = 10000
        self.wait_time = 1800

    def request_retry_count(self):
        count = self.r.get(self.rrc_key)
        if count is None:
            self.r.set(self.rrc_key, 1)
        else:
            self.r.set(self.rrc_key, int(count) + 1)

    def request_403_count(self):
        count = self.r.get(self.f_t_o)
        if count is None:
            self.r.set(self.f_t_o, 1)
        else:
            self.r.set(self.f_t_o, int(count) + 1)

    def request_200_count(self):
        count = self.r.get("200")
        if count is None:
            self.r.set("200", 1)
        else:
            self.r.set("200", int(count) + 1)

    def check_403_count(self):
        count = self.r.get(self.f_t_o)
        if count is None:
            count = 0
        if int(count) > self.f_t_o_max or int(count) == 1:
            self.update_data_wait()

    def check_retry(self):
        count = self.r.get(self.rrc_key)
        print(datetime.datetime.now(), "retry count:", count)
        if count is None:
            if int(self.r.llen(self.key_name)) == 0:
                IGLogin().re_login()
                self.insert_data()
            else:
                return
        else:
            count = int(count)
            if count >= self.rrc_max:
                print(datetime.datetime.now(), "更新")
                self.update_data_wait()
                # self.rrc_wait()

    def insert_data(self):
        data = json.load(open(self.login_data_path, "r"))["data"]
        if int(self.r.llen(self.key_name)) < len(data):
            data = json.load(open(self.login_data_path, "r"))["data"]
            self.r.delete(self.key_name)
            for i in data:
                self.r.lpush(self.key_name, json.dumps(i))

    def update_data(self):
        self.r.delete(self.key_name)
        IGLogin().re_login()
        self.insert_data()
        self.r.delete(self.rrc_key)

    def update_data_wait(self):
        # self.r.delete(self.key_name)
        IGLogin().re_login()
        time.sleep(self.wait_time)
        self.r.delete(self.key_name)
        self.insert_data()
        self.r.delete("200")
        self.r.delete(self.rrc_key)

    def rrc_wait(self):
        self.r.delete(self.key_name)
        time.sleep(self.wait_time)
        self.insert_data()
        self.r.delete("200")
        self.r.delete(self.rrc_key)

    def get_info(self):
        while True:
            count = int(self.r.llen(self.key_name))
            if count != 0:
                break
            else:
                time.sleep(10)
        index = random.choice(range(count))
        return json.loads(self.r.lrange(self.key_name, index, index)[0])

    def stop_crawler(self, crawler):
        count = 0
        while True:
            crawler.engine.pause()
            if int(self.r.llen(self.key_name)) != 0:
                crawler.engine.unpause()
                if count > 0:
                    return False
                else:
                    return True
            else:
                time.sleep(10)
                count += 1


if __name__ == "__main__":
    rli = RedisLoginInfo()
    rli.insert_data()
    # IGLogin().re_login()
