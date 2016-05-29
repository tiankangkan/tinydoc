# -*- coding: UTF-8 -*-

"""
Desc: setting file.
Note:

---------------------------------------
# 2016/04/02   kangtian         created

"""

import os
import platform
from k_util.file_op import make_sure_file_dir_exists

SYSTEM = platform.system()

BASE_DIR = os.path.dirname(__file__)

FONT_DIR = os.path.join(BASE_DIR, 'res', 'font')


if 'windows' in SYSTEM:
    DATA_DIR = 'D:\\tinydoc\\data\\'
else:
    DATA_DIR = '/data/tinydoc/data/'

if 'windows' in SYSTEM:
    TEMP_DIR = 'D:\\tinydoc\\tmp\\'
else:
    TEMP_DIR = '/data/tinydoc/tmp/'

make_sure_file_dir_exists(DATA_DIR, is_dir=True)
make_sure_file_dir_exists(TEMP_DIR, is_dir=True)
