#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from tools.redis_the_popper import RedisPoper

rp = RedisPoper()
while True:
    rp.poper()
