#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from tools.data_insert import insert_all
import os

PATH = os.path.dirname(os.path.abspath(__file__))
data_path = PATH + "/data"
files = os.listdir(data_path)
for file in files:
    file_path = os.path.abspath(data_path + "/" + file)
    print(file_path)
    insert_all(file_path)
