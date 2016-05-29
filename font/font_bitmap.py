# -*- coding: UTF-8 -*-

"""
Desc: manage fonts.
Note:

---------------------------------------
# 2016/04/03   kangtian         created

"""

import time
import os
import gzip
import cPickle as Pickle
from image.base import PosRect, RGB, Palette
from image.block import Block
from font.font_char import FontChar


class GB18030(object):
    def __init__(self, b0=None, b1=None, b2=None, b3=None):
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.b3 = b3

    def to_unicode(self):
        l = [self.b0, self.b1, self.b2, self.b3]
        array = bytearray([b for b in l if b is not None])
        try:
            ch = array.decode(encoding='gb18030')
        except UnicodeDecodeError:
            ch = None
            raise
        return ch

    def from_unicode(self, ch):
        bytes = bytearray('%s' % ch, encoding="gb18030")
        length = len(bytes)
        self.b0 = bytes[0] if length > 0 else None
        self.b1 = bytes[1] if length > 1 else None
        self.b2 = bytes[2] if length > 2 else None
        self.b3 = bytes[3] if length > 3 else None
        return self


class FontBitmapPos(object):
    SET_TYPE_GB = 'GB'
    SET_TYPE_ASCII = 'ASCII'

    def __init__(self, y, x, set_type):
        """
        :param y: y pos of bitmap
        :param x: x pos of bitmap
        :Note: self.type: 'GB' or 'ASCII'
        :return:
        """
        self.x = x
        self.y = y
        self.set_type = set_type

    def __str__(self):
        if self.set_type == self.SET_TYPE_ASCII:
            return '%s (%s)' % (self.set_type, self.x)
        else:
            return '%s (%s, %s)' % (self.set_type, self.x, self.y)


class FontBitmap(object):
    """
    Define of C:
        struct Font_info F;
        F.flag = 'F';
        strcpy(F.name, "kang");
        F.blank = 64;
        F.char_height = 256;
        F.char_width = 256;
        F.line_width = 8;
        F.char_num_of_line = 128;
        F.rows_ASCII = 1;
        F.rows_GB = 128;
    Note:
        ASCII 字符在前, GB 字符在后
        与四周边框留下 blank 距离
        GB 与 ASCII 留下 blank 距离
    """
    default_layout = dict(
        blank=64,
        char_height=256,
        char_width=256,
        line_width=8,
        char_num_of_line=128,
        rows_ASCII=1,
        rows_GB=128
    )

    def __init__(self, font_path, layout_setting=default_layout, do_load=False):
        """
        :layout blank: 留白长度
        :layout char_height: 字符高度
        :layout char_width: 字符宽度
        :layout line_width: 线条宽度
        :layout char_num_of_line: 每行字符数
        :layout rows_ASCII: ASCII 行数
        :layout rows_GB:
        :return:
        """
        self.blank = layout_setting['blank']
        self.char_height = layout_setting['char_height']
        self.char_width = layout_setting['char_width']
        self.line_width = layout_setting['line_width']
        self.char_num_of_line = layout_setting['char_num_of_line']
        self.rows_ASCII = layout_setting['rows_ASCII']
        self.rows_GB = layout_setting['rows_GB']
        self.font_path = font_path
        self.font_block = Block()
        if not os.path.exists(font_path):
            raise IOError('Font path not exists: %s' % font_path)
        if do_load:
            self.load_bitmap_to_block()

    @property
    def is_block_load(self):
        return self.font_block.inst is not None

    def load_bitmap_to_block(self, font_path=None):
        font_path = font_path or self.font_path
        self.font_block = Block().from_file(font_path)
        self.font_path = font_path

    def get_bitmap_pos_of_ch(self, ch):
        """
        :Note: 这里返回的位置,
            对于 GB 码:
                y 轴为高位(区码), x 轴为低位(位码), 范围均为是 0 ~ 127.
                '啊' 位于 16区01位, 在这里为 47区32位, 因为gb2312从1开始, 而这里从0开始, 并且区多了32个.
            对于 ASCII 码:
                y 轴为 0, x 轴为其值本身.
        :param ch:
        :return:
        """
        gb = GB18030().from_unicode(ch)
        if gb.b2 is not None:
            raise Exception("Char out of range, Bitmap Font only support 128*128")
        b_high = gb.b0
        b_low = gb.b1
        if gb.b1:
            x = b_low - 0x80 - 1
            y = b_high - 0x80 - 1
        else:
            x, y = gb.b0, 0
        set_type = FontBitmapPos.SET_TYPE_ASCII if gb.b1 is None else FontBitmapPos.SET_TYPE_GB
        pos = FontBitmapPos(y=y, x=x, set_type=set_type)
        return pos

    def get_ch_of_bitmap_pos(self, pos):
        if pos.set_type == FontBitmapPos.SET_TYPE_ASCII:
            ch = GB18030(b0=pos.x).to_unicode()
        else:
            y = pos.y + 0x80 + 1
            x = pos.x + 0x80 + 1
            ch = GB18030(b0=y, b1=x).to_unicode()
        return ch

    def get_rect_of_char_in_bitmap(self, ch, border=5):
        pos = self.get_bitmap_pos_of_ch(ch)
        p0_x = self.blank + self.line_width - 1
        p0_y = self.blank + self.line_width - 1
        if pos.set_type == FontBitmapPos.SET_TYPE_GB:
            p0_y += self.blank + self.rows_ASCII*(self.line_width + self.char_height) + self.line_width
        top = p0_y + pos.y * (self.line_width + self.char_height)
        left = p0_x + pos.x * (self.line_width + self.char_width)
        bottom = top + self.char_height
        right = left + self.char_width
        top, left = top + border, left + border
        bottom, right = bottom - border, right - border
        rect = PosRect(top=top, left=left, bottom=bottom, right=right)
        return rect

    def get_block_of_char(self, ch):
        if not self.is_block_load:
            self.load_bitmap_to_block()
        rect = self.get_rect_of_char_in_bitmap(ch)
        if rect.is_full_ok:
            block = self.font_block.cut_with_rect(rect)
        else:
            block = None
        return block

    def load_ch_of_pos_x_y(self, ch_set, x, y, char_set_type):
            pos = FontBitmapPos(x=x, y=y, set_type=char_set_type)
            ch = self.get_ch_of_bitmap_pos(pos)
            if ch:
                block = self.get_block_of_char(ch)
                is_blank = block.is_fill_with_color(Palette.white, is_exact=True, sample_percent=None)
                print 'ch: %s, blank: %s' % (ch, is_blank)
                if not is_blank:
                    ch_set[ch] = FontChar(ch=ch, block=block, do_generate_info=True)

    def get_char_set(self):
        t_start = time.time()
        ch_set = dict()
        for x in range(0, 126):
            for y in range(0, 126):
                print x, y
                self.load_ch_of_pos_x_y(ch_set, x, y, char_set_type=FontBitmapPos.SET_TYPE_GB)
            if x % 10 == 0:
                print "<FontBitmap.get_char_set> process: %3d/%3d (%.2f%%)" % (x, 127, x*100/127.0)
        for x in range(128):
            self.load_ch_of_pos_x_y(ch_set, x, 0, char_set_type=FontBitmapPos.SET_TYPE_ASCII)
        print "<FontBitmap.get_char_set> Cost Time %s sec." % (time.time() - t_start)
        return ch_set

if __name__ == '__main__':
    ch = u" "
    font = FontBitmap(font_path='/Users/kangtian/Documents/Master/tinydoc/res/font/hunlu.bmp')
    print font.get_rect_of_char_in_bitmap(ch)
    # ch_block = font.get_block_of_char(ch)
    # print ch_block.get_pix(x=10, y=10)
    # print ch_block.is_fill_with_color(RGB(255, 255, 255))
    # print 'Mode: %s' % ch_block.inst.mode
    # ch_block.to_file('/Users/kangtian/Documents/Master/tinydoc/render/char_zi.bmp')
    t_start = time.time()
    ch_set = font.get_char_set()
    Pickle.dump(ch_set, open('ch_set_get_data.dat', 'wb'))
    print 'Keys Num: %s' % len(ch_set.keys())
    print "Cost Time %s sec." % (time.time() - t_start)

