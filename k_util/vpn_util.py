# -*- coding: UTF-8 -*-

"""
Desc: vpn util.
Note:

---------------------------------------
# 2016/05/09   kangtian         created

"""

import requests

url = 'http://kuaibao.qq.com/s/20160509A0711800'
resp = requests.get(url)
print resp.text

for i in range(100):
    resp = requests.get(url)
