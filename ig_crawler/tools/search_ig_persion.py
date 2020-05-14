#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import requests
import json
import random
import urllib
import time


class SearchIG:
    def __init__(self):
        self.login_info_list = json.load(open("./login_data.json"))["data"]
        self.API_URL = 'https://i.instagram.com/api/v1/'
        self.SIG_KEY_VERSION = '4'

    def following_url(self, rank_token, user_id, max_id=""):
        url = self.API_URL + 'friendships/' + str(user_id) + '/following/?'
        query_string = {'ig_sig_key_version': self.SIG_KEY_VERSION,
                        'rank_token': rank_token}
        if max_id:
            query_string['max_id'] = max_id
        url += urllib.parse.urlencode(query_string)
        return url

    def follower_url(self, rank_token, user_id, max_id=""):
        if max_id == '':
            return self.API_URL + 'friendships/' + str(user_id) + '/followers/?rank_token=' + rank_token
        else:
            return self.API_URL + 'friendships/' + str(
                user_id) + '/followers/?rank_token=' + str(rank_token) + '&max_id=' + str(max_id)

    def following(self, user_id, user_list=[], next_max_id=""):
        login_info = random.choice(self.login_info_list)
        response = requests.get(self.following_url(login_info["rank_token"], user_id, next_max_id),
                                headers=login_info["headers"],
                                cookies=login_info["cookies"])
        time.sleep(2)
        try:
            json_response = json.loads(response.text)
        except:
            print(response.text)
            return user_list
        if json_response["status"] == 'fail':
            if json_response[
                "message"] == "Please wait a few minutes before you try again.":
                self.login_info_list.remove(login_info)
                self.following(user_id, user_list, next_max_id)
            else:
                return user_list
        next_max_id = json_response["next_max_id"]
        for user in json_response["users"]:
            user_list.append(user)
        print(len(user_list))
        if next_max_id is not None:
            self.following(user_id, user_list, next_max_id)
        else:
            return user_list

    def follower(self, user_id, user_list=[], next_max_id=""):
        login_info = random.choice(self.login_info_list)
        response = requests.get(self.follower_url(login_info["rank_token"], user_id, next_max_id),
                                headers=login_info["headers"],
                                cookies=login_info["cookies"])
        time.sleep(2)
        try:
            json_response = json.loads(response.text)
        except:
            print(response.text)
            return user_list
        if json_response["status"] == 'fail':
            if json_response[
                "message"] == "Please wait a few minutes before you try again.":
                # self.login_info_list.reomve(login_info)
                self.follower(user_id, user_list, next_max_id)
            else:
                return user_list
        next_max_id = json_response["next_max_id"]
        for user in json_response["users"]:
            user_list.append(user)
        print(len(user_list))
        if next_max_id is not None:
            self.follower(user_id, user_list, next_max_id)
        else:
            return user_list

    def user_data(self, user_name):
        login_info = random.choice(self.login_info_list)
        url = self.API_URL + 'users/' + str(user_name) + '/usernameinfo/'
        response = requests.get(url, headers=login_info["headers"], cookies=login_info["cookies"])
        user_data = json.loads(response.text)
        print(user_data)
        if user_data["status"] == 'fail':
            return False
        is_private = user_data["user"]['is_private']
        user_id = user_data["user"]["pk"]
        if is_private is True:
            following = []
            follower = []
        else:
            following = self.following(user_id)
            follower = self.follower(user_id)
        data = {
            "user_data": user_data,
            "following": following,
            "follower": follower,
        }
        print(data)
        return data
