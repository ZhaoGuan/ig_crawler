#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import json
import InstagramAPI.InstagramAPI as IAPI
import requests
import os

result = []
PATH = os.path.dirname(os.path.abspath(__file__))
login_data_path = PATH + "/../login_data.json"


def login(user, password):
    api = IAPI(user, password)
    if api.login():
        result.append(
            {"headers": dict(api.s.headers), "cookies": requests.utils.dict_from_cookiejar(api.s.cookies),
             "rank_token": api.rank_token})


def re_login():
    user_info = json.load(open(login_data_path))["data"]
    for user in user_info:
        user_name = user["cookies"]["ds_user"]
        if "cdc." in user_name or "ccp." in user_name:
            password = "gz19891020"
        else:
            password = "abc123456"
        login(user_name, password)
    with open(login_data_path, "w") as f:
        data = {'data': result}
        json.dump(data, f)
