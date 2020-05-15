#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import pymysql
import json
from tools.search_ig_persion import SearchIG


class IGDB:
    def __init__(self):
        self.db = pymysql.connect("localhost", "root", "gz19891020", "ig", charset="utf8mb4")
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


'''
向mysql插入数据
'''


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


class UserData:
    def __init__(self):
        self.ig = IGDB()
        self.s_ig = SearchIG()
        self.up_ig = UpdataIGDB()
        self.is_research = False

    def user_data_base_username(self, username):
        user_data_result = {}
        result = self.ig.run_select_sql(self.ig.get_user_base_user_name(str(username)))
        if len(result) == 1:
            user_data = result[0]
            user_data_result['id'] = user_data[0]
            user_data_result['user_name'] = user_data[1]
            user_data_result['full_name'] = user_data[2]
            if user_data[3] == 0:
                user_data_result['is_private'] = False
            else:
                user_data_result['is_private'] = True
            if user_data[4] == 0:
                user_data_result['is_business'] = False
            else:
                user_data_result['is_business'] = True
            user_data_result['profile_pic_url'] = user_data[5]
            user_data_result['hd_profile_pic_url_info'] = json.loads(user_data[6])
            user_data_result["following_count"] = user_data[7]
            user_data_result["follower_count"] = user_data[8]
            return user_data_result
        else:
            if self.is_research:
                return self.user_data_base_username_research(username)
            else:
                return False

    def user_data_base_username_research(self, username):
        user_data = self.s_ig.user_data(username)
        if user_data is False:
            return False
        master = user_data["user_data"]["user"]["pk"]
        insert_user = self.up_ig.insert_user(user_data["user_data"]["user"])
        if insert_user:
            self.up_ig.delete_user_follower(master)
            self.up_ig.delete_user_following(master)
            if user_data["follower"]:
                for follower in user_data["follower"]:
                    self.up_ig.insert_user_follower(master, follower["pk"], follower["username"])
            if user_data["following"]:
                for following in user_data["following"]:
                    self.up_ig.insert_user_following(master, following["pk"], following["username"])
            return self.user_data_base_username(username)
        else:
            return False

    def user_data_base_user_id(self, user_id):
        user_data_result = {}
        result = self.ig.run_select_sql(self.ig.get_user_base_user_id(str(user_id)))
        if len(result) == 1:
            user_data = result[0]
            user_data_result['id'] = user_data[0]
            user_data_result['user_name'] = user_data[1]
            user_data_result['full_name'] = user_data[2]
            if user_data[3] == 0:
                user_data_result['is_private'] = False
            else:
                user_data_result['is_private'] = True
            if user_data[4] == 0:
                user_data_result['is_business'] = False
            else:
                user_data_result['is_business'] = True
            user_data_result['profile_pic_url'] = user_data[5]
            user_data_result['hd_profile_pic_url_info'] = json.loads(user_data[6])
            user_data_result["following_count"] = user_data[7]
            user_data_result["follower_count"] = user_data[8]
            return user_data_result
        else:
            if self.is_research:
                return self.user_data_base_user_id_research(user_id)
            else:
                return False

    def user_data_base_user_id_research(self, user_id):
        user_name = self.get_username_from_following_or_follower(user_id)
        if user_name:
            user_data = self.s_ig.user_data(user_name)
            if user_data is False:
                return False
            master = user_data["user_data"]["user"]["pk"]
            inster_user = self.up_ig.insert_user(user_data["user_data"]["user"])
            if inster_user:
                self.up_ig.delete_user_follower(master)
                self.up_ig.delete_user_following(master)
                if user_data["follower"]:
                    for follower in user_data["follower"]:
                        self.up_ig.insert_user_follower(master, follower["pk"], follower["username"])
                if user_data["following"]:
                    for following in user_data["following"]:
                        self.up_ig.insert_user_following(master, following["pk"], following["username"])
                return self.user_data_base_username(user_id)
            else:
                return False
        else:
            return False

    def following(self, master_id):
        result = self.ig.run_select_sql(self.ig.get_following_base_master(str(master_id)))
        if result:
            i_following = [i[1] for i in result]
            return i_following
        else:
            return False

    def follower(self, master_id):
        result = self.ig.run_select_sql(self.ig.get_follower_base_master(str(master_id)))
        if result:
            i_follower = [i[1] for i in result]
            return i_follower
        else:
            return False

    def get_username_following(self, following):
        result = self.ig.run_select_sql(self.ig.get_username_from_following(following))
        if len(result) > 0:
            return result[0][0]
        else:
            return False

    def get_username_follower(self, follower):
        result = self.ig.run_select_sql(self.ig.get_username_from_following(follower))
        if len(result) > 0:
            return result[0][0]
        else:
            return False

    def get_username_from_following_or_follower(self, user_id):
        following_result = self.get_username_following(user_id)
        follower_result = self.get_username_follower(user_id)
        if follower_result or follower_result:
            if follower_result:
                return follower_result
            else:
                return following_result
        else:
            return False


"""抄的"""


def mapping_sort_from_list(data: list):
    value = set(data)
    times = []
    index = []
    for i in value:
        times.append(data.count(i))
        index.append(data.index(i))
    res = []
    for i in zip(value, times, index):
        res.append(i)
    res = sorted(res, key=lambda x: (-x[1], x[2]))  # 负号表示从大到小，因为默认是从小到大
    ans = []
    for item in res:
        ans += [item[0]] * item[1]
    result = {}
    for i in ans:
        if i not in result:
            result[i] = 1
        else:
            result[i] += 1
    return result


class Statistics:
    def __init__(self):
        self.ud = UserData()
        self.interesting_min = 2
        self.s_ig = SearchIG()
        self.up_ig = UpdataIGDB()

    def user_id_base_username(self, username):
        user_date = self.ud.user_data_base_username(username)
        if user_date:
            return user_date["id"]
        else:
            return False

    def following(self, username):
        user_id = self.user_id_base_username(username)
        following = self.ud.following(user_id)
        if user_id and following:
            result = [self.ud.user_data_base_user_id(i) for i in following if i]
            # result = [i["user_name"] for i in result if i]
            return result
        else:
            return False

    def follower(self, username):
        user_id = self.user_id_base_username(username)
        follower = self.ud.follower(user_id)
        if user_id and follower:
            result = [self.ud.user_data_base_user_id(i) for i in follower if i]
            # result = [i["user_name"] for i in result if i]
            return result
        else:
            return False

    def check_friends(self, username):
        user_id = self.user_id_base_username(username)
        if user_id:
            return self.check_friends_by_user_id(user_id)
        else:
            return False

    def check_friends_by_user_id(self, user_id):
        follower = self.ud.follower(user_id)
        following = self.ud.following(user_id)
        if following and follower:
            # result = [i for i in follower if i in following]
            result = [self.ud.user_data_base_user_id(i) for i in follower if i in following]
            # result = [i["user_name"] for i in result if i]
            return result
        else:
            return False

    def interesting_user(self, username):
        user_id = self.user_id_base_username(username)
        if user_id:
            # return self.interesting_user_by_user_id(user_id)
            return self._interesting_user(username, user_id)
        else:
            return False

    def interesting_user_by_user_id(self, user_id):
        following = self.ud.following(user_id)
        if following:
            result_id_list = []
            for i_following_id in following:
                temp_id_following = self.ud.following(i_following_id)
                if temp_id_following:
                    [result_id_list.append(temp_id_following_id) for temp_id_following_id in temp_id_following]
            result = [k for k, v in mapping_sort_from_list(result_id_list).items() if
                      int(v) > self.interesting_min]
            for follow in following:
                try:
                    result.remove(follow)
                except:
                    pass
            try:
                result.remove(user_id)
            except:
                pass
            result = [self.ud.user_data_base_user_id(follow_id) for follow_id in result]
            result = [i["user_name"] for i in result if i]
            return result
        else:
            return False

    def _interesting_user(self, user_name, user_id):
        my_following = self.following(user_name)
        temp_result = []
        relational = {}
        if my_following:
            my_following_id_list = [i for i in my_following if i]
            for my_f in my_following_id_list:
                my_f_fs = self.following(my_f["user_name"])
                if my_f_fs:
                    self.my_friend_friends(my_f, my_f_fs, temp_result, relational)
            result = [k for k, v in mapping_sort_from_list(temp_result).items() if
                      int(v) >= 2]
            for my_f in my_following:
                try:
                    result.remove(my_f["id"])
                except:
                    pass
            try:
                result.remove(user_id)
            except:
                pass
            relational_mapping = {}
            self.relational_mapping(relational_mapping, result, relational)
            result = {"users": [self.ud.user_data_base_user_id(k) for k in result],
                      "relational": relational_mapping}
            return result
        else:
            return False

    def who_may_know(self, username):
        user_id = self.user_id_base_username(username)
        if user_id:
            return self.who_may_know_by_user_id(user_id)
        else:
            return False

    def who_may_know_by_user_id(self, user_id):
        my_friends = self.check_friends_by_user_id(user_id)
        temp_result = []
        relational = {}
        if my_friends:
            my_friend_id_list = [i for i in my_friends if i]
            for my_f in my_friend_id_list:
                my_f_fs = self.check_friends_by_user_id(my_f["id"])
                if my_f_fs:
                    self.my_friend_friends(my_f, my_f_fs, temp_result, relational)
            result = [k for k, v in mapping_sort_from_list(temp_result).items() if
                      int(v) >= 2]
            for my_f in my_friend_id_list:
                try:
                    result.remove(my_f["id"])
                except:
                    pass
            try:
                result.remove(user_id)
            except:
                pass
            relational_mapping = {}
            self.relational_mapping(relational_mapping, result, relational)
            # result = {"users": [k for k in result], "relational": relational_mapping}
            result = {"users": [self.ud.user_data_base_user_id(k) for k in result],
                      "relational": relational_mapping}
            # result = {"users": [i["user_name"] for i in result["users"] if i], "relational": relational_mapping}
            return result

        else:
            return False

    def my_friend_friends(self, my_f, my_f_fs, temp_result, relational):
        for my_f_f in my_f_fs:
            if my_f_f:
                my_f_f_id = my_f_f["id"]
                my_f_f_name = my_f_f["user_name"]
                temp_result.append(my_f_f_id)
                if my_f_f_id not in relational:
                    relational[my_f_f_id] = [[my_f["user_name"], my_f_f_name]]
                else:
                    if [my_f["user_name"], my_f_f_name] not in relational[my_f_f_id]:
                        relational[my_f_f_id].append([my_f["user_name"], my_f_f_name])

    def relational_mapping(self, relational_mapping, result, relational):
        for k in result:
            relational_mapping[k] = relational[k]


if __name__ == "__main__":
    insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1583654591094.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1583905563229.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1583905676517.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1583911151801.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1583919252147.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1583922743768.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1583927435552.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1583981826966.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1583985304902.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1583985645676.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1583985845455.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1584063040029.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1584081787560.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1584096958534.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1584102440057.json")
    # insert_all("/Users/gz/Desktop/project/ig_crawler/ig_crawler/1584107899235.json")
    s = Statistics()
    # a = s.following("yuankeke001")
    # a = s.follower("yuankeke001")
    # a = s.user_id_base_username("yuankeke001")
    # a = s.check_friends("yuankeke001")
    a = s.who_may_know("yuankeke001")
    # a = s.interesting_user("yuankeke001")
    # a = s.check_friends("yuankeke001")
    print(a)
    # ud = UserData()
    # a = ud.get_username_following("181603649")
    # print(a)
