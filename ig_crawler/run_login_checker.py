#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from tools.redis_login_checker import RedisChecker

rp = RedisChecker()
while True:
    try:
        rp.login_checker()
    except:
        pass
