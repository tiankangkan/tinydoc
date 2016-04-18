# -*- coding: UTF-8 -*-

"""
Desc: string op.
Note:

---------------------------------------
# 2016/04/04   kangtian         created

"""

import os


def make_sure_file_dir_exists(file_path):
    if os.path.isdir(file_path):
        path_dir = file_path
    else:
        path_dir = os.path.dirname(file_path)
    if path_dir and not os.path.exists(path_dir):
        os.makedirs(path_dir)
