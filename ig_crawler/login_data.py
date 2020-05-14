#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import InstagramAPI.InstagramAPI as IAPI
import requests
import json
import decimal

user_info = []


def login(user, password):
    api = IAPI(user, password)
    if api.login():
        user_info.append(
            {"headers": dict(api.s.headers), "cookies": requests.utils.dict_from_cookiejar(api.s.cookies),
             "rank_token": api.rank_token})


for user in range(0, 130):
    try:
        login("cdc.cdc.cdc" + str(user), "gz19891020")
    except:
        print("cdc.cdc.cdc" + str(user), "login fail")
for user in range(0, 130):
    try:
        login("ccp.ccp." + str(user), "gz19891020")
    except:
        print("ccp.ccp." + str(user), "login fail")
# for user in ["cdc.cdc.cdc.2.", "cdc.cdc.cdc.3.", "cdc.cdc.cdc.4."]:
#     for nu in range(0, 130):
#         try:
#             login("cdc.cdc." + str(nu), "gz19891020")
#         except:
#             print(str(user), "login fail")

with open("./login_data.json", "w") as f:
    print(user_info)
    print(len(user_info))
    data = {'data': user_info}
    json.dump(data, f)
# with open("./login_data.json") as f:
#     print(len(json.load(f)))
