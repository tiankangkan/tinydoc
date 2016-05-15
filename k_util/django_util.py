# -*- coding: UTF-8 -*-

"""
Desc: django util.
Note:

---------------------------------------
# 2016/04/17   kangtian         created

"""


def get_request_body(request, raw=None):
    """
    :param request:
    :param raw: raw = 'GET' | 'POST'
    :return:
    """

    body_dict = dict()
    if 'GET' == raw or 'POST' == raw:
        d = getattr(request, raw)
        if d:
            for key in d:
                body_dict[key] = d[key]
    else:
        if request.GET:
            for key in request.GET:
                body_dict[key] = request.GET[key]
        if request.POST:
            for key in request.POST:
                body_dict[key] = request.POST[key]
    return body_dict




