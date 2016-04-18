# -*- coding: UTF-8 -*-

"""
Desc: define of things.

---------------------------------------
# 2016/04/02   kangtian         created

"""
import copy
from collections import namedtuple

RGB = namedtuple('RGB', ['R', 'G', 'B'])


class Palette(object):
    white = RGB(255, 255, 255)
    black = RGB(0, 0, 0)
    red = RGB(255, 0, 0)
    green = RGB(0, 255, 0)
    blue = RGB(0, 0, 255)
    yellow = RGB(255, 255, 0)
    magenta = RGB(255, 0, 255)
    cyan = RGB(0, 255, 255)
    gray = RGB(109, 109, 109)
    skyblue = RGB(116, 195, 232)
    chocolate = RGB(200, 84, 10)
    seashell = RGB(255, 243, 233)
    purple = RGB(108, 0, 110)


class ColorMode(object):
    RGB = 'RGB'
    BGR = 'BGR'
    RGBX = 'RGBX'
    PALETTE = 'PALETTE'
    GREYSCALE = 'GREYSCALE'
    BIT1 = 'BIT1'


class PosBase(object):

    def copy(self):
        return copy.deepcopy(self)

    def to_tuple(self):
        t = ()
        return t

    def __str__(self):
        return str(self.to_tuple())


class PosRect(PosBase):
    def __init__(self, top=None, right=None, bottom=None, left=None):
        self.top, self.bottom = top, bottom
        self.left, self.right = left, right

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def width(self):
        return self.right - self.left

    def from_point_pair(self, smaller, bigger):
        if isinstance(smaller, tuple):
            smaller = PosPoint2D(x=smaller[0], y=smaller[1])
        if isinstance(bigger, tuple):
            bigger = PosPoint2D(x=bigger[0], y=bigger[1])
        self.top = smaller.y
        self.left = smaller.x
        self.right = bigger.x
        self.bottom = bigger.y
        return self

    def start_from_zero(self):
        self.top = 0
        self.left = 0
        self.right = None
        self.bottom = None
        return self

    def to_tuple(self):
        rect = (self.top, self.right, self.bottom, self.left)
        return rect

    def to_points(self):
        points = (self.left, self.top, self.right, self.bottom)
        return points

    def __str__(self):
        return '[(%s, %s), (%s, %s)]' % (self.left, self.top, self.right, self.bottom)

    @property
    def is_full_ok(self):
        if self.bottom is not None and self.right is not None and self.top is not None and self.left is not None:
            return True
        else:
            return False

    @property
    def is_part_ok(self):
        if self.top is not None and self.left is not None:
            return True
        else:
            return False

    def translate(self, x, y):
        self.top += y
        self.bottom += y
        self.left += x
        self.right += x
        return self

    def make_include_another(self, another):
        another.top = max(self.top, another.top)
        another.bottom = min(self.bottom, another.bottom)
        another.left = max(self.left, another.left)
        another.right = min(self.right, another.right)

        another.top = min(another.top, another.bottom)
        another.left = min(another.left, another.right)
        another.bottom = max(another.top, another.bottom)
        another.right = max(another.left, another.right)

    def delta_size(self, d_width, d_height):
        self.top -= d_height
        self.bottom += d_height
        self.right += d_width
        self.left -= d_width
        self.fix()

    def fix(self):
        if self.top > self.bottom:
            center = (self.top + self.bottom) / 2
            self.top, self.bottom = center, center
        if self.left > self.right:
            center = (self.left + self.right) / 2
            self.left, self.right = center, center


class PosPoint2D(PosBase):
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return PosPoint2D(x=x, y=y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return PosPoint2D(x=x, y=y)

    def to_tuple(self):
        point = (self.x, self.y)
        return point

    def __str__(self):
        return str(self.to_tuple())