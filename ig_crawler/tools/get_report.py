#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from tools.user_mysql import Statistics
from tools.googlesheet import GoogleSheet

s = Statistics()
GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1pzxzgzs3lxhcLv134itOfE_upqxvjHISAMx-i2QwaGs')


def following_report(user):
    s.ud.is_research = True
    following = s.following(user)
    data = []
    for i in following:
        if i:
            data.append(
                [i["user_name"], '=image("%s")' % i["profile_pic_url"], i["following_count"], i["follower_count"],
                 i["is_private"], i["is_business"]])
    sheet = GS.update_sheet(user, "A3:F", data)
    print(sheet)


def follower_report(user):
    s.ud.is_research = True
    follower = s.follower(user)
    data = []
    for i in follower:
        if i:
            data.append(
                [i["user_name"], '=image("%s")' % i["profile_pic_url"], i["following_count"], i["follower_count"],
                 i["is_private"], i["is_business"]])
    sheet = GS.update_sheet(user, "G3:L", data)
    print(sheet)


def friends_report(user):
    s.ud.is_research = False
    friends = s.check_friends(user)
    data = []
    for i in friends:
        if i:
            data.append(
                [i["user_name"], '=image("%s")' % i["profile_pic_url"]])
    sheet = GS.update_sheet(user, "M3:N", data)
    print(sheet)


def who_maybe_konw_report(user):
    s.ud.is_research = False
    who_may_know = s.who_may_know(user)
    data = []
    relational = who_may_know["relational"]
    for i in who_may_know["users"]:
        if i:
            i_id = i["id"]
            relational_from = []
            for i_relational in relational[i_id]:
                relational_from.append(i_relational[0])
            data.append(
                [i["user_name"], '=image("%s")' % i["profile_pic_url"], str(relational_from)])
    sheet = GS.update_sheet(user, "O3:Q", data)
    print(sheet)


def interesting_report(user):
    s.ud.is_research = False
    interesting_user = s.interesting_user(user)
    data = []
    relational = interesting_user["relational"]
    for i in interesting_user["users"]:
        if i:
            i_id = i["id"]
            relational_from = []
            for i_relational in relational[i_id]:
                relational_from.append(i_relational[0])
            data.append(
                [i["user_name"], '=image("%s")' % i["profile_pic_url"], i["is_private"], i["is_business"],
                 str(relational_from)])
    sheet = GS.update_sheet(user, "R3:Y", data)
    print(sheet)


def run_report(name):
    following_report(name)
    follower_report(name)
    friends_report(name)
    who_maybe_konw_report(name)
    interesting_report(name)


if __name__ == "__main__":
    # name = "ter.zhao"
    # name = "zhangmela"
    # name = "jinnii"
    # name = "japhethguo"
    # name = "pmbian"
    for name in ["ter.zhao", "zhangmela", "jinnii", "japhethguo", "pmbian"]:
        run_report(name)
