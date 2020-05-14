#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from scrapy import cmdline

name = 'ig'
cmd = 'scrapy crawl {0} -s JOBDIR=crawls/ig'.format(name)
cmdline.execute(cmd.split())
'''scrapy crawl ig'''