# -*- coding: UTF-8 -*-

"""
Desc: django util.
Note:

---------------------------------------
# 2016/04/30   kangtian         created

"""
from hashlib import md5


def gen_md5(content_str):
    m = md5()
    m.update(content_str)
    return m.hexdigest()
