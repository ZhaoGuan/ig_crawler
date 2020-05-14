#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import os

PATH = os.path.dirname(os.path.abspath(__file__))
GOOGLE_PATH = "operaxx1:/ig/20200514"
data_path = PATH + "/../data"


def upload():
    files = os.listdir(data_path)
    for file in files:
        file_path = os.path.abspath(data_path + "/" + file)
        print(file_path)
        fsize = round(os.path.getsize(file_path) / float(1024 * 1024))
        if fsize >= 100:
            result = os.popen("rclone copy local:{source} {dest}".format(source=file_path, dest=GOOGLE_PATH))
            print(result)


if __name__ == "__main__":
    upload()
