# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class IgCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


import json
import time
import os


class JsonPipeline(object):
    def __init__(self):
        self.file_name = './data/' + str(int(round(time.time() * 1000))) + '.json'
        self.file = open(self.file_name, 'wb')
        self.file_size = 1

    def process_item(self, item, spider):
        fsize = round(os.path.getsize(self.file_name) / float(1024 * 1024))
        if fsize < self.file_size:
            line = json.dumps(dict(item)) + "\n"
            self.file.write(line.encode('utf-8'))
        else:
            self.file.close()
            self.file_name = './data/' + str(int(round(time.time() * 1000))) + '.json'
            self.file = open(self.file_name, 'wb')
            line = json.dumps(dict(item)) + "\n"
            self.file.write(line.encode('utf-8'))
        return item

    def close_spider(self, spider):
        self.file.close()
