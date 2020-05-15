#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import pymysql
import json
import os
from tools.mysql_config import MYSQL_HOST, PASS_WORD


class IGDB:
    def __init__(self):
        self.db = pymysql.connect(MYSQL_HOST, "root", PASS_WORD, "ig", charset="utf8mb4")
        self.cursor = self.db.cursor()

    def insert_user(self, user_data):
        user_id = user_data["pk"]
        user_name = user_data["username"]
        full_name = pymysql.escape_string(user_data["full_name"])
        is_private = user_data["is_private"]
        is_business = user_data["is_business"]
        profile_pic_url = user_data["profile_pic_url"]
        hd_profile_pic_url_info = json.dumps(user_data["hd_profile_pic_url_info"])
        following_count = user_data["following_count"]
        follower_count = user_data["follower_count"]
        sql = """
        INSERT INTO user_data(user_id,user_name,full_name,is_private,is_business,profile_pic_url,hd_profile_pic_url_info,following_count,follower_count) 
        VALUES ('%s','%s',\'%s\',%s,%s,'%s','%s','%s','%s')
                 """ % (
            user_id, user_name, full_name, is_private, is_business, profile_pic_url, hd_profile_pic_url_info,
            following_count, follower_count)
        return sql

    def insert_following(self, master, following, following_username):
        sql = """
                INSERT INTO following(master_id,following,following_username) 
                VALUES ('%s','%s','%s')
                         """ % (master, following, following_username)
        return sql

    def insert_follower(self, master, follower, follower_username):
        sql = """
                INSERT INTO follower(master_id,follower,follower_username) 
                VALUES ('%s','%s','%s')
                         """ % (master, follower, follower_username)
        return sql

    def delete_master_following(self, master):
        sql = "DELETE FROM following WHERE master_id = %s" % (master)
        return sql

    def delete_master_follower(self, master):
        sql = "DELETE FROM follower WHERE master_id = %s" % (master)
        return sql

    def get_master_base_following(self, following):
        sql = "SELECT * FROM following WHERE fowllowing='%s'" % (following)
        return sql

    def get_following_base_master(self, master):
        sql = "SELECT * FROM following WHERE master_id='%s'" % (master)
        return sql

    def get_master_base_follower(self, follower):
        sql = "SELECT * FROM follower WHERE fowllower='%s'" % (follower)
        return sql

    def get_follower_base_master(self, master):
        sql = "SELECT * FROM follower WHERE master_id='%s'" % (master)
        return sql

    def get_user_base_user_name(self, user_name):
        sql = "SELECT * FROM user_data WHERE user_name='%s'" % (user_name)
        return sql

    def get_user_base_user_id(self, user_id):
        sql = "SELECT * FROM user_data WHERE user_id='%s'" % (user_id)
        return sql

    def get_username_from_following(self, user_id):
        sql = "SELECT following_username FROM `following` WHERE  `following`='%s'" % (
            user_id)
        return sql

    def get_username_from_follower(self, user_id):
        sql = "SELECT follower_username FROM `follower` WHERE  `follower`='%s'" % (
            user_id)
        return sql

    def run_insert_delete_sql(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            # print(sql)
            self.db.rollback()
            return False

    def run_select_sql(self, sql):
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.db.commit()
        return result


class UpdataIGDB:
    def __init__(self):
        self.igdb = IGDB()

    def insert_user(self, userdata):
        return self.igdb.run_insert_delete_sql(self.igdb.insert_user(userdata))

    def insert_user_following(self, master, following, following_username):
        self.igdb.run_insert_delete_sql(self.igdb.insert_following(master, following, following_username))

    def insert_user_follower(self, master, follower, follower_username):
        self.igdb.run_insert_delete_sql(self.igdb.insert_follower(master, follower, follower_username))

    def delete_user_following(self, master):
        self.igdb.run_insert_delete_sql(self.igdb.delete_master_following(master))

    def delete_user_follower(self, master):
        self.igdb.run_insert_delete_sql(self.igdb.delete_master_follower(master))

    def get_username_following(self, following):
        self.igdb.run_select_sql(self.igdb.get_username_from_following(following))

    def get_username_follower(self, following):
        self.igdb.run_select_sql(self.igdb.get_username_from_following(following))


def insert_all(json_file):
    ig = UpdataIGDB()
    count = 0
    with open(json_file) as f:
        for i in f:
            count += 1
            i = json.loads(i, encoding="utf-8")
            master = i["user_data"]["user"]["pk"]
            inster_user = ig.insert_user(i["user_data"]["user"])
            if inster_user:
                ig.delete_user_follower(master)
                ig.delete_user_following(master)
                for follower in i["follower"]:
                    ig.insert_user_follower(master, follower["pk"], follower["username"])
                for following in i["following"]:
                    ig.insert_user_following(master, following["pk"], following["username"])
    print(count)


