# -*- coding: UTF-8 -*-

"""
Desc: string op.
Note:

---------------------------------------
# 2016/04/02   kangtian         created

"""

encoding_list = ['UTF-8', 'gbk']


def to_unicode(s):
    if not isinstance(s, basestring):
        raise ValueError('Not string, type is %s : %s' % (type(s), s))
    if isinstance(s, unicode):
        return s + ''
    unicode_s = s
    if isinstance(s, str):
        for encoding in encoding_list:
            try:
                unicode_s = s.decode(encoding=encoding)
            except UnicodeDecodeError:
                continue
            break
    if not isinstance(unicode_s, unicode):
        raise Exception('Can not convert to unicode: %s' % s)
    return unicode_s


def to_utf_8(s):
    s_unicode = to_unicode(s)
    return s_unicode.encode('utf-8')    # not support unicode


def is_chinese_char(ch):
    ch = to_unicode(ch)
    return u'\u2e80' <= ch <= u'\uffff'


def is_ascii_char(ch):
    ch = to_unicode(ch)
    return u'\u0000' <= ch <= u'\u007f'


def is_cn_symbol(ch):
    ch = to_unicode(ch)
    cn_symbol = u'－＝（）＊&……％¥＃@！——＋［］；’、，。／｀～《》？：“｜｛｝'
    return ch in cn_symbol


if __name__ == '__main__':
    print [u'（']
    print is_chinese_char('（')
