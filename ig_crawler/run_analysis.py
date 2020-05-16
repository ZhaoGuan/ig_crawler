#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from tools.new_analysis import friends_following_top_report, my_friends_know_a_friends_top_report, \
    friends_friend_follower_top_report, friends_friends_top_report, same_friends_report

for i in ["zhangmela", "alina.archer"]:
    friends_friends_top_report(i)
    friends_friend_follower_top_report(i)
    friends_following_top_report(i)
    same_friends_report(i)
    my_friends_know_a_friends_top_report(i)
