# -*- coding: UTF-8 -*-

"""
Desc: doc page.
Note: the base unit is 'mm' but not 'pix'.

---------------------------------------
# 2016/04/02   kangtian         created

"""

import copy
from collections import namedtuple

PointTuple = namedtuple('PointTuple', ['x', 'y', 'z'])
RectTuple = namedtuple('RectTuple', ['top', 'right', 'bottom', 'left'])


class Measure(object):
    PIX = 'pix'
    MM = 'mm'

    def __init__(self, inner_value=None):
        self.inner_unit = self.PIX
        self.inner_value = inner_value
        self._pix_per_mm = 25

    @property
    def pix_per_mm(self):
        return self._pix_per_mm

    @pix_per_mm.setter
    def pix_per_mm(self, pix_per_mm):
        self._pix_per_mm = pix_per_mm

    @property
    def v(self):
        return self.inner_value

    @v.setter
    def v(self, value):
        self.inner_value = value

    def set_mm(self, value):
        self.mm = value
        return self

    @property
    def mm(self):
        return self.inner_value / float(self.pix_per_mm)

    @mm.setter
    def mm(self, value):
        self.inner_value = value * self.pix_per_mm

    @property
    def pix(self):
        return self.inner_value

    @pix.setter
    def pix(self, pix):
        self.inner_value = pix
        if self.pix_per_mm:
            self.inner_value = float(pix) / self.pix_per_mm
        else:
            raise Exception("pix_per_mm is not defined, please use function set_pix_per_mm().")

    def set_pix(self, value):
        self.pix = value
        return self

    def __repr__(self):
        return self.inner_value


class MeasurePoint2D(object):
    def __init__(self, x, y):
        self.x, self.y = Measure(x), Measure(y)

    @property
    def to_tuple(self):
        point = PointTuple(self.x.v, self.y.v)
        return point

    def __repr__(self):
        return str(self.to_tuple)


class MeasureSize(object):
    def __init__(self, width, height):
        self.width, self.height = Measure(width), Measure(height)

    @property
    def to_tuple(self):
        rect = RectTuple(self.width.v, self.height.v)
        return rect


class MeasureRect(object):
    def __init__(self, top, right, bottom, left):
        self.top, self.bottom = Measure(top), Measure(bottom)
        self.left, self.right = Measure(left), Measure(right)

    @property
    def to_tuple(self):
        rect = RectTuple(self.top.v, self.right.v, self.bottom.v, self.left.v)
        return rect

    def __repr__(self):
        return str(self.to_tuple)


class FontSize(Measure):
    """
    Default unit is point.
    """
    mm_per_point = 0.35146

    def __init__(self, font_size):
        mm_value = self.mm_per_point * font_size
        super(FontSize, self).__init__(inner_value=mm_value)

    @property
    def get_point_size(self):
        return int(self.inner_value / float(self.mm_per_point))
