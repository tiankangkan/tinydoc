# -*- coding: UTF-8 -*-

"""
Desc: django util.
Note:

---------------------------------------
# 2016/04/17   kangtian         created

"""

import json
import urllib, urllib2
import traceback
from k_util.str_op import to_utf_8


def post_request(url, data=None, method='POST'):
    data = data or dict()
    if isinstance(data, basestring):
        data = to_utf_8(data)
    if method == 'POST':
        if isinstance(data, dict):
            data = urllib.urlencode(data)
        req = urllib2.Request(url, data=data)
    else:
        req = urllib2.Request(url, headers=data)
    try:
        resp = urllib2.urlopen(req).read()
    except Exception, e:
        print traceback.format_exc(e)
        raise Exception("error occur with url: %s" % url)
    return resp


