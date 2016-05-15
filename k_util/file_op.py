# -*- coding: UTF-8 -*-

"""
Desc: file op.
Note:

---------------------------------------
# 2016/04/04   kangtian         created

"""

import os
import shutil


def make_sure_file_dir_exists(file_path, is_dir=False):
    if is_dir or os.path.isdir(file_path):
        path_dir = file_path
    else:
        path_dir = os.path.dirname(file_path)
    if path_dir and not os.path.exists(path_dir):
        os.makedirs(path_dir)


def move_file(src_path, dst_path):
    path_dir = os.path.dirname(dst_path)
    if path_dir and not os.path.exists(path_dir):
        os.makedirs(path_dir)
    shutil.copy(src_path, dst_path)
    os.remove(src_path)


def read_file_to_lines(file_path):
    lines = open(file_path, 'r').read().replace('\r', '').split('\n')
    return lines


def clear_dir(dir_path):
    shutil.rmtree(dir_path)


def get_file_list_of_dir(dir_path):
    file_list = list()
    for dir_root, dirs, file_names in os.walk(dir_path):
        for file_name in file_names:
            file_list.append(os.path.join(dir_root, file_name))
    return file_list
