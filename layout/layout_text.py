# -*- coding: UTF-8 -*-

"""
Desc: doc text.
Note:

---------------------------------------
# 2016/04/04   kangtian         created

"""

from layout.measure import Measure, FontSize
from image.base import Palette
from layout.layout_element import LayoutBase, Direction


class TextDirection(object):
    def __init__(self, char_direction, line_direction):
        self.char_direction = char_direction
        self.line_direction = line_direction


class DocCharBase(LayoutBase):
    def __init__(self, ch, size, color):
        super(DocCharBase, self).__init__()
        self.ch = ch
        self.size = size
        self.color = color


class DocChar(DocCharBase):
    def __init__(self, ch, size=FontSize(12), color=Palette.white):
        super(DocChar, self).__init__(ch=ch, size=size, color=color)


class DocTextBase(LayoutBase):
    def __init__(self, text, font_size, font_color, bg_color, text_direction):
        super(DocTextBase, self).__init__()
        self.text = text
        self.font_size = font_size
        self.font_color = font_color
        self.bg_color = bg_color
        self.text_direction = text_direction


class DocText(DocTextBase):
    def __init__(self, text='', font_size=None, font_color=None, bg_color=None, text_direction=None):
        font_size = font_size or FontSize(12)
        font_color = font_color or Palette.black
        bg_color = bg_color or Palette.white
        text_direction = text_direction or TextDirection(Direction.TO_RIGHT, Direction.TO_BOTTOM)
        super(DocText, self).__init__(text=text, font_size=font_size, font_color=font_color,
                                      bg_color=bg_color, text_direction=text_direction)

