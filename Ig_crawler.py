#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from InstagramAPI import InstagramAPI
import time
import json
import threadpool


class IG:
    def __init__(self):
        self.api = InstagramAPI("zhao.guan.wuren", "gz19891020")
        self.api.login()
        self.wait_time = 5
        print(self.api.s.headers)
        print(self.api.s.cookies.RequestsCookieJar())

    def is_flowing(self):
        self.api.getUserFollowings(self.api.username_id)
        status = self.api.LastJson["status"]
        if status is "ok":
            user_list = self.user_list(self.api.getUserFollowings(self.api.username_id))
            return [i["pk"] for i in user_list]
        else:
            return False

    def search_user(self, name):
        self.api.searchUsername(name)
        status = self.api.LastJson["status"]
        if status == "ok":
            return self.api.LastJson
        else:
            print(self.api.LastJson)
            return False

    def get_followers(self, user_id):
        self.api.getUserFollowers(user_id)
        status = self.api.LastJson["status"]
        if status == "ok":
            user_list = self.user_list(self.api.getUserFollowers(user_id))
            return user_list
        else:
            print(self.api.LastJson)
            return False

    def get_following(self, user_id):
        self.api.getUserFollowings(user_id)
        status = self.api.LastJson["status"]
        if status == "ok":
            user_list = self.user_list(self.api.getUserFollowings(user_id))
            return user_list
        else:
            print(self.api.LastJson)
            return False

    def follow(self, user_id):
        self.api.follow(user_id)

    def user_list(self, quary_funciton):
        the_list = []
        for i in self.api.LastJson["users"]:
            the_list.append(i)
        try:
            next_max_id = self.api.LastJson["next_max_id"]
        except:
            return the_list
        while True:
            print(len(the_list))
            if next_max_id is not None:
                time.sleep(self.wait_time)
                quary_funciton
                for i in self.api.LastJson["users"]:
                    the_list.append(i)
                next_max_id = self.api.LastJson["next_max_id"]
            else:
                break
        return the_list


class IGCrawler:
    def __init__(self):
        self.ig = IG()
        self.is_flowing = self.ig.is_flowing()

    def get_user(self, name):
        user_date = self.ig.search_user(name)
        user_id = user_date["user"]["pk"]
        is_private = user_date["user"]["is_private"]
        if is_private is True and user_id not in self.is_flowing:
            print(name, user_id, "is not following!")
            self.ig.follow(user_id)
        following = self.ig.get_following(user_id)
        follower = self.ig.get_followers(user_id)
        print(name)
        print(user_date)
        print("follower", follower)
        print("following", following)


if __name__ == "__main__":
    ig = IGCrawler()
    ig.get_user("lagi.viraall")
    # ig.get_user("therealmafud")
    # ig.get_user("deva.awr")
    # cases = ["lagi.viraall", "therealmafud", "deva.awr"]
    # pool = threadpool.ThreadPool(20)
    # pool_requests = threadpool.makeRequests(ig.get_user, cases)
    # [pool.putRequest(req) for req in pool_requests]
    # pool.wait()
