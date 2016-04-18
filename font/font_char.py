# -*- coding: UTF-8 -*-

"""
Desc: char of font.
Note:

---------------------------------------
# 2016/04/02   kangtian         created

"""

from image.base import Palette, PosRect
from k_util.str_op import is_ascii_char, is_chinese_char, is_cn_symbol, to_unicode
from layout.layout_base import Direction


class FontChar(object):
    def __init__(self, ch, block, do_generate_info=True, mbr_rect=None):
        self.ch = to_unicode(ch)
        self.block = block
        self.mbr_rect = mbr_rect
        if do_generate_info:
            self.generate_info()

    def generate_info(self):
        self.mbr_rect = self.mbr_rect or self.block.get_mbr_rect(Palette.white, sample_percent=None)

    def is_en_char(self):
        return is_ascii_char(self.ch)

    def is_cn_char(self):
        return is_chinese_char(self.ch)

    def is_cn_symbol(self):
        return is_cn_symbol(self.ch)

    def get_valid_rect(self, direction):
        valid_rect = None
        if direction.is_horizontal:
            mbr = self.mbr_rect
            if self.is_cn_char() and not self.is_cn_symbol():
                valid_rect = mbr.copy()
            elif self.is_cn_char() and self.is_cn_symbol():
                valid_rect = PosRect(top=0, bottom=self.block.height, left=mbr.left, right=mbr.right)
            elif self.is_en_char():
                valid_rect = PosRect(top=0, bottom=self.block.height, left=mbr.left, right=mbr.right)
            else:
                raise ValueError('can not get char type.')
        elif direction.is_vertical:
            mbr = self.mbr_rect
            if self.is_cn_char() and not self.is_cn_symbol():
                valid_rect = mbr.copy()
            elif self.is_cn_char() and self.is_cn_symbol():
                valid_rect = mbr.copy()
            elif self.is_en_char():
                valid_rect = mbr.copy()
            else:
                raise ValueError('can not get char type.')

        return valid_rect

