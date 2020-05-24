#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import requests
import json
import os
import time

host = "http://83.136.180.216:9999"
upload_max = 100


class InsertNeo4j:
    def __init__(self):
        self.host = "http://83.136.180.216:9999"
        self.upload_max = 100
        self.insert_count = 0

    def insert(self, path):
        url = host + "/instagram/user/saveRelation"
        with open(path, "r") as f:
            for i in f:
                self.insert_count += 1
                i.replace("\n", "")
                json_data = json.loads(i)
                user_data = json_data["user_data"]
                following = json_data["following"]
                follower = json_data["follower"]
                while True:
                    if len(following) == 0 and len(follower) == 0:
                        break
                    if len(follower) > upload_max:
                        temp_follower = follower[:upload_max]
                        follower = follower[upload_max:]
                    else:
                        temp_follower = follower
                        follower = []
                    if len(following) > upload_max:
                        temp_following = follower[:upload_max]
                        following = following[upload_max:]
                    else:
                        temp_following = following
                        following = []
                    post_json = {
                        "data": {
                            "pk": user_data["user"]["pk"],
                            "username": user_data["user"]["username"],
                            "fullname": user_data["user"]["full_name"],
                            "isPrivate": user_data["user"]["is_private"],
                            "isBusiness": user_data["user"]["full_name"],
                            "followerCount": user_data["user"]["follower_count"],
                            "followingCount": user_data["user"]["following_count"],
                            "profilePicUrl": user_data["user"]["profile_pic_url"],
                            "following": [
                                {"pk": _following["pk"],
                                 "username": _following["username"],
                                 "fullname": _following["full_name"],
                                 "isPrivate": _following["is_private"],
                                 "isBusiness": _following["full_name"],
                                 "profilePicUrl": _following["profile_pic_url"], } for _following in temp_following
                            ],
                            "follower": [
                                {"pk": _follower["pk"],
                                 "username": _follower["username"],
                                 "fullname": _follower["full_name"],
                                 "isPrivate": _follower["is_private"],
                                 "isBusiness": _follower["full_name"],
                                 "profilePicUrl": _follower["profile_pic_url"], } for _follower in temp_follower
                            ]
                        }
                    }
                    response = requests.post(url, json=post_json)
                    # print(response.status_code)
                    # print(response.text)
                    # if json.loads(response.text)["code"] != "200":
                    #     print(post_json)
                print(self.insert_count)

    def find_friend(self, user_id):
        url = host + "/instagram/user/findFirend"
        post_json = {"data": user_id}
        begin = time.time()
        response = requests.post(url, json=post_json)
        print(response.status_code)
        print(response.text)
        print(time.time() - begin)


if __name__ == "__main__":
    ins_neo4j = InsertNeo4j()
    PATH = os.path.dirname(os.path.abspath(__file__))
    data_path = PATH + "/../data"
    files = os.listdir(data_path)
    for file in files:
        file_path = os.path.abspath(data_path + "/" + file)
        ins_neo4j.insert(file_path)
    print("最后完成了:", ins_neo4j.insert_count)
