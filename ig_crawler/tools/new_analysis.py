#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import pymysql
import json
from tools.search_ig_persion import SearchIG
from tools.user_mysql import Statistics
from tools.googlesheet import GoogleSheet
import copy
from tools.mysql_config import MYSQL_HOST, PASSWORD


class IGDB:
    def __init__(self):
        self.db = pymysql.connect(MYSQL_HOST, "root", PASSWORD, "ig", charset="utf8mb4")
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
        sql = "SELECT master_id,following,following_username FROM following WHERE fowllowing='%s'" % (following)
        return sql

    def get_following_base_master(self, master):
        sql = "SELECT master_id,following,following_username FROM following WHERE master_id='%s'" % (master)
        return sql

    def get_master_base_follower(self, follower):
        sql = "SELECT master_id,follower,follower_username FROM follower WHERE fowllower='%s'" % (follower)
        return sql

    def get_follower_base_master(self, master):
        sql = "SELECT master_id,follower,follower_username FROM follower WHERE master_id='%s'" % (master)
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

    def get_username_following(self, master):
        self.igdb.run_select_sql(self.igdb.get_username_from_following(master))

    def get_username_follower(self, master):
        self.igdb.run_select_sql(self.igdb.get_username_from_follower(master))


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
            i_following = [{"id": i[1], "name": i[2]} for i in result]
            return i_following
        else:
            return False

    def follower(self, master_id):
        result = self.ig.run_select_sql(self.ig.get_follower_base_master(str(master_id)))
        if result:
            i_follower = [{"id": i[1], "name": i[2]} for i in result]
            return i_follower
        else:
            return False

    def friends(self, master_id):
        following = self.following(master_id)
        follower = self.follower(master_id)
        if follower is False or following is False:
            return False
        id_list = []
        user_mapping = {}
        for i in following:
            t_id = i["id"]
            t_name = i["name"]
            if t_id not in id_list:
                user_mapping[t_id] = t_name
        for i in follower:
            t_id = i["id"]
            t_name = i["name"]
            if t_id not in id_list:
                user_mapping[t_id] = t_name
        following_id = [i["id"] for i in following]
        follower_id = [i["id"] for i in follower]
        friends = set(following_id).intersection(set(follower_id))
        friends = [{"id": i, "name": user_mapping[i]} for i in friends]
        return friends

    def t_friends(self, master_id):
        following = self.following(master_id)
        follower = self.follower(master_id)
        if follower is False or following is False:
            return False
        id_list = []
        user_mapping = {}
        for i in following:
            t_id = i["id"]
            t_name = i["name"]
            if t_id not in id_list:
                user_mapping[t_id] = t_name
        for i in follower:
            t_id = i["id"]
            t_name = i["name"]
            if t_id not in id_list:
                user_mapping[t_id] = t_name
        following_id = [i["id"] for i in following]
        follower_id = [i["id"] for i in follower]
        friends = []
        for i in following_id:
            if i not in friends and i in follower_id:
                friends.append(i)
        friends = [{"id": i, "name": user_mapping[i]} for i in friends]
        return friends

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


def intersection(r, m):
    result = list(set(r).intersection(set(m)))
    return result


def union(r, m):
    return list(set(r).union(set(m)))


def sort_by_value(d):
    items = d.items()
    backitems = [[v[1], v[0]] for v in items]
    backitems.sort(reverse=True)
    return [backitems[i][1] for i in range(0, len(backitems))]


class Analysis:
    def __init__(self):
        self.igdb = IGDB()
        self.ud = UserData()

    def my_all(self, name):
        user_data = self.ud.user_data_base_username(name)
        id = user_data["id"]
        followings = self.ud.following(id)
        following_id = [f["id"] for f in followings]
        followers = self.ud.follower(id)
        follower_id = [f["id"] for f in followers]
        friends = self.ud.friends(id)
        friends_id = [f["id"] for f in friends]
        all_user = union(follower_id, following_id)
        all_data = {}
        result = {}
        for user in all_user:
            t_follower = self.ud.follower(user)
            if t_follower is False:
                continue
            t_follower = [f["id"] for f in t_follower]
            t_following = self.ud.following(user)
            if t_following is False:
                continue
            t_following = [f["id"] for f in t_following]
            t_friend = [f["id"] for f in self.ud.friends(user)]
            all_data[user] = {'follower': t_follower, "following": t_following, "friends": t_friend}
        for id, data in all_data.items():
            follower_follower = intersection(follower_id, data["follower"])
            follower_follower = len(follower_follower)
            following_follower = intersection(following_id, data["follower"])
            following_follower = len(following_follower)
            follower_following = intersection(follower_id, data["following"])
            follower_following = len(follower_following)
            following_following = intersection(following_id, data["following"])
            following_following = len(following_following)
            friends_friends = intersection(friends_id, data["friends"])
            friends_friends = len(friends_friends)
            data = self.ud.user_data_base_user_id(id)
            name = data["user_name"]
            full_name = data["full_name"]
            data = {"name": name, "full_name": full_name, "follower_follower": follower_follower,
                    "following_follower": following_follower,
                    "following_following": following_following, "follower_following": follower_following,
                    "friends_friends": friends_friends}
            result[id] = data
        return result

    def friends_group(self, name):
        user_data = self.ud.user_data_base_username(name)
        my_id = user_data["id"]
        friends = self.ud.friends(my_id)
        friends_id = [f["id"] for f in friends]
        all_user = friends_id
        all_data = {my_id: friends_id}
        intersection_data = {}
        for user in all_user:
            t_friend = self.ud.friends(user)
            if t_friend is False:
                continue
            t_friend = [f["id"] for f in t_friend]
            try:
                t_friend.remove(my_id)
            except:
                pass
            all_data[user] = t_friend
        for id, data in all_data.items():
            data = intersection(friends_id, data)
            if len(data) == 0:
                continue
            intersection_data[id] = data
        print(all_data)
        print(intersection_data)
        result = []
        for user_id, data in intersection_data.items():
            up = [user_id]
            self.get_group(my_id, result, up, data, intersection_data, all_data)
        print(result)
        the_result = []
        for i in result:
            temp = []
            for e in i:
                user_data = self.ud.user_data_base_user_id(e)
                name = user_data["user_name"]
                full_name = user_data["full_name"]
                temp.append(name + " " + full_name)
            the_result.append(temp)
        return the_result

    def get_group(self, my_id, result, up, data, intersection_data, all_data):
        temp_up = copy.deepcopy(up)
        while data:
            print("up", temp_up)
            print("data", data)
            now = data.pop(0)
            count = 0
            if now in all_data.keys():
                for have in temp_up:
                    if now in all_data[have] and have in all_data[now]:
                        count += 1
                    else:
                        print("err", now, have)
            if now in intersection_data.keys() and count == len(temp_up):
                temp = []
                for i in data:
                    if i in all_data[now] and i in intersection_data and now in all_data[i]:
                        count = 0
                        # 和之前的都是好友关系
                        for have in temp_up:
                            if i in all_data[have] and have in all_data[i]:
                                count += 1
                            else:
                                print("err", i, have)
                        if count == len(temp_up):
                            temp.append(i)
                if len(temp) > 0:
                    print("up", temp_up)
                    print("now", now)
                    print("temp", temp)
                    temp_up.append(now)
                    self.get_group(my_id, result, temp_up, temp, intersection_data, all_data)
                else:
                    temp_up.append(my_id)
                    temp_up = list(set(temp_up))
                    temp_up.sort()
                    if temp_up not in result and len(temp_up) > 3:
                        print("result", temp_up)
                        result.append(temp_up)
                    break
            if data:
                self.get_group(my_id, result, temp_up, data, intersection_data, all_data)

    def same_friends(self, name):
        user_data = self.ud.user_data_base_username(name)
        my_id = user_data["id"]
        friends = self.ud.friends(my_id)
        friends_id = [f["id"] for f in friends]
        all_user = friends_id
        all_data = {}
        intersection_data = {}
        for user in all_user:
            t_friend = self.ud.friends(user)
            if t_friend is False:
                continue
            t_friend = [f["id"] for f in t_friend]
            try:
                t_friend.remove(my_id)
            except:
                pass
            all_data[user] = t_friend
        for id, data in all_data.items():
            data = intersection(friends_id, data)
            if len(data) == 0:
                continue
            intersection_data[id] = data
        return intersection_data

    def friends_friends_top(self, name):
        user_data = self.ud.user_data_base_username(name)
        if user_data is False:
            print(name)
        my_id = user_data["id"]
        friends = self.ud.friends(my_id)
        friends_id = [f["id"] for f in friends]
        following = self.ud.following(my_id)
        following_id = [f["id"] for f in following]
        all_user = friends_id
        all_data = {}
        for user in all_user:
            t_friend = self.ud.friends(user)
            if t_friend is False:
                continue
            t_friend = [f["id"] for f in t_friend]
            try:
                t_friend.remove(my_id)
            except:
                pass
            all_data[user] = t_friend
        all_friend_friends = []
        for user_id, data in all_data.items():
            for data_ in data:
                all_friend_friends.append(data_)
        _all_friend_friends = list(set(all_friend_friends).difference(set(friends_id)))
        friend_friend_list = []
        friend_friend_mapping = {}
        for friend_friend in all_friend_friends:
            if friend_friend in _all_friend_friends and friend_friend not in following_id:
                if friend_friend in friend_friend_list:
                    friend_friend_mapping[friend_friend] += 1
                else:
                    friend_friend_list.append(friend_friend)
                    friend_friend_mapping[friend_friend] = 1
        return {"list": sort_by_value(friend_friend_mapping), "mapping": friend_friend_mapping}

    def friends_friend_follower_top(self, name):
        user_data = self.ud.user_data_base_username(name)
        my_id = user_data["id"]
        friends = self.ud.friends(my_id)
        friends_id = [f["id"] for f in friends]
        following = self.ud.following(my_id)
        following_id = [f["id"] for f in following]
        all_user = friends_id
        all_data = {}
        for user in all_user:
            t_friend = self.ud.friends(user)
            if t_friend is False:
                continue
            try:
                t_friend.remove(my_id)
            except:
                pass
            t_f_list = []
            for t_f in t_friend:
                t_f_d = self.ud.user_data_base_user_id(t_f["id"])
                if t_f_d:
                    t_f_list.append({"id": t_f["id"], "follower_count": t_f_d["follower_count"]})
            all_data[user] = t_f_list
        result = {}
        for user_id, data in all_data.items():
            for i in data:
                if i["id"] not in friends_id and i not in following_id and i["id"] not in result.keys():
                    result[i["id"]] = i["follower_count"]
        return {"list": sort_by_value(result), "mapping": result}

    def friends_following_top(self, name):
        user_data = self.ud.user_data_base_username(name)
        my_id = user_data["id"]
        friends = self.ud.friends(my_id)
        friends_id = [f["id"] for f in friends]
        following = self.ud.following(my_id)
        following_id = [f["id"] for f in following]
        all_user = friends_id
        all_data = {}
        for user in all_user:
            t_following = self.ud.following(user)
            if t_following is False:
                continue
            t_following = [f["id"] for f in t_following]
            try:
                t_following.remove(my_id)
            except:
                pass
            all_data[user] = t_following
        result = {}
        result_list = []
        for user_id, data in all_data.items():
            for i in data:
                if i not in friends_id and i not in following_id:
                    if i in result_list:
                        result[i] += 1
                    else:
                        result_list.append(i)
                        result[i] = 1
        return {"list": sort_by_value(result), "mapping": result}

    def my_friends_know_a_friends_top(self, name):
        user_data = self.ud.user_data_base_username(name)
        my_id = user_data["id"]
        friends = self.ud.friends(my_id)
        friends_id = [f["id"] for f in friends]
        following = self.ud.following(my_id)
        following_id = [f["id"] for f in following]
        all_user = friends_id
        all_data = {}
        for user in all_user:
            t_friend = self.ud.friends(user)
            if t_friend is False:
                continue
            t_friend = [f["id"] for f in t_friend]
            try:
                t_friend.remove(my_id)
            except:
                pass
            all_data[user] = t_friend
        result = {}
        for user_id, data in all_data.items():
            t_user_friends_list = []
            for t_user_id, t_data in all_data.items():
                if t_user_id != user_id:
                    for t_f in t_data:
                        t_user_friends_list.append(t_f)
            try:
                t_user_friends_list.remove(user_id)
            except:
                pass
            t_result = {}
            t_result_list = []
            for f_id in t_user_friends_list:
                if f_id in data:
                    if f_id in t_result_list:
                        t_result[f_id] += 1
                    else:
                        t_result_list.append(f_id)
                        t_result[f_id] = 1
            result[user_id] = {"list": sort_by_value(t_result), "mapping": t_result}
        return result


def my_all_report(user):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '12MmAW4HNl4B3bkFMYI14Em53exW3EL_1sgCRSp4UIW0')
    analysis = Analysis()
    result = analysis.my_all(user)
    data = []
    for id, i in result.items():
        if i:
            data.append(
                [i["name"], i["full_name"], i["follower_follower"], i["following_follower"], i["following_following"],
                 i["follower_following"], i["friends_friends"]])
    sheet = GS.update_sheet(user, "A2:G", data)
    print(sheet)


def my_group(user):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1S6tTRyRExGxyGU807gLRmvxYiNmBA5UAin131FTt4LA')
    analysis = Analysis()
    data = analysis.friends_group(user)
    result = []
    for v in data:
        temp = []
        for e in v:
            temp.append(e["name"] + " " + e["full_name"])
        result.append(temp)
    sheet = GS.update_sheet(user + "_test1", "A2:Z", result)
    print(sheet)


def my_group_test(user):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1S6tTRyRExGxyGU807gLRmvxYiNmBA5UAin131FTt4LA')
    analysis = Analysis()
    data = analysis.friends_group(user)
    sheet = GS.update_sheet(user + "_test1", "A2:Z", data)
    print(sheet)


def friends_friends_top_report(name):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1YLA3wxZwZJSM_yjwi4Sey1L1-y__ufwovw6mPurApCc')
    ud = UserData()
    analysis = Analysis()
    data = analysis.friends_friends_top(name)
    data = data["mapping"]
    result = []
    for k, v in data.items():
        u_d = ud.user_data_base_user_id(k)
        if u_d is False:
            continue
        n = u_d["user_name"]
        f_n = u_d["full_name"]
        result.append([n + " " + f_n, v])
    sheet = GS.update_sheet(name + "_好友的好友推荐", "A1:Z", result)
    print(sheet)


def friends_following_top_report(name):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1YLA3wxZwZJSM_yjwi4Sey1L1-y__ufwovw6mPurApCc')
    ud = UserData()
    analysis = Analysis()
    data = analysis.friends_following_top(name)
    data = data["mapping"]
    result = []
    for k, v in data.items():
        u_d = ud.user_data_base_user_id(k)
        if u_d is False:
            continue
        n = u_d["user_name"]
        f_n = u_d["full_name"]
        result.append([n + " " + f_n, v])
    sheet = GS.update_sheet(name + "_好友following推荐", "A1:Z", result)
    print(sheet)


def friends_friend_follower_top_report(name):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1YLA3wxZwZJSM_yjwi4Sey1L1-y__ufwovw6mPurApCc')
    ud = UserData()
    analysis = Analysis()
    data = analysis.friends_friend_follower_top(name)
    data = data["mapping"]
    result = []
    for k, v in data.items():
        u_d = ud.user_data_base_user_id(k)
        if u_d is False:
            continue
        n = u_d["user_name"]
        f_n = u_d["full_name"]
        result.append([n + " " + f_n, v])
    sheet = GS.update_sheet(name + "_好友的好友根据follower推荐", "A1:Z", result)
    print(sheet)


def same_friends_report(name):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1YLA3wxZwZJSM_yjwi4Sey1L1-y__ufwovw6mPurApCc')
    ud = UserData()
    analysis = Analysis()
    data = analysis.same_friends(name)
    result = []
    for k, v in data.items():
        u_d = ud.user_data_base_user_id(k)
        if u_d is False:
            continue
        n = u_d["user_name"]
        f_n = u_d["full_name"]
        temp = [n + " " + f_n]
        for i in v:
            t_u_d = ud.user_data_base_user_id(i)
            if t_u_d is False:
                continue
            t_n = t_u_d["user_name"]
            t_f_n = t_u_d["full_name"]
            temp.append(t_n + " " + t_f_n)
        result.append(temp)
    sheet = GS.update_sheet(name + "_共同好友", "A1:ZZ", result)
    print(sheet)


def my_friends_know_a_friends_top_report(name):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1YLA3wxZwZJSM_yjwi4Sey1L1-y__ufwovw6mPurApCc')
    ud = UserData()
    analysis = Analysis()
    data = analysis.my_friends_know_a_friends_top(name)
    result = []
    for k, v in data.items():
        u_d = ud.user_data_base_user_id(k)
        if u_d is False:
            continue
        n = u_d["user_name"]
        f_n = u_d["full_name"]
        temp = [n + " " + f_n]
        if v["mapping"]:
            for i, c in v["mapping"].items():
                t_u_d = ud.user_data_base_user_id(i)
                if t_u_d is False:
                    continue
                t_n = t_u_d["user_name"]
                t_f_n = t_u_d["full_name"]
                temp.append(t_n + " " + t_f_n + " " + str(c))
        result.append(temp)
    sheet = GS.update_sheet(name + "_a_好友认识我好友", "A1:ZZ", result)
    print(sheet)


if __name__ == "__main__":
    """velvet_cat yuankeke001 tsuziai zhangmela terzhao alina.archer"""
    "_好友的好友推荐"
    "_好友following推荐"
    "_共同好友"
    "_好友的好友根据follower推荐"
    "_a_好友认识我好友"
    analysis = Analysis()
    data = analysis.friends_friends_top('tsuziai')
    # for i in ["velvet_cat", "yuankeke001", "tsuziai", "zhangmela", "ter.zhao", "alina.archer"]:
    for i in ["alina.archer", 'velvet_cat', 'tsuziai']:
        friends_friends_top_report(i)
        friends_friend_follower_top_report(i)
        friends_following_top_report(i)
        same_friends_report(i)
        my_friends_know_a_friends_top_report(i)
