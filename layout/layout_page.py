# -*- coding: UTF-8 -*-

"""
Desc: doc page.
Note: the base unit is 'mm' but not 'pix'.

---------------------------------------
# 2016/04/02   kangtian         created

"""

from collections import namedtuple
from image.base import ColorMode
from measure import MeasureSize
from measure import Measure as M


class PageSize(MeasureSize):
    page_size_type_mapping = {
        'A0': dict(width=841, height=1189),
        'A1': dict(width=594, height=841),
        'A2': dict(width=420, height=594),
        'A3': dict(width=297, height=420),
        'A4': dict(width=210, height=297),
        'A5': dict(width=148, height=210),
    }

    def __init__(self, page_size_type=None, width=M(210), height=M(297)):
        if page_size_type is not None:
            d = self.page_size_type_mapping[page_size_type]
            width, height = d['width'], d['height']
        super(PageSize, self).__init__(width=width, height=height)


class PageEdge(object):
    page_edge_type_mapping = {
        'normal': dict(top=0.0855, bottom=0.0855, left=0.151, right=0.151),
        'narrow': dict(top=0.0427, bottom=0.0427, left=0.0427, right=0.0427),
        'broad': dict(top=0.0855, bottom=0.0855, left=0.241, right=0.241),
    }

    def __init__(self, page_edge_type=None, top=0.0855, bottom=0.0855, left=0.151, right=0.151):
        if page_edge_type is not None:
            d = self.page_edge_type_mapping[page_edge_type]
            top, bottom = d['top'], d['bottom']
            left, right = d['left'], d['right']
        self.top, self.bottom = top, bottom
        self.left, self.right = left, right


class DocPageBase(object):
    """
    Page Size(mm):
        A0: 841*1189,
        A1: 594*841,
        A2: 420*594,
        A3: 297*420,
        A4: 210*297,
        A5: 148*210,
    """

    def __init__(self, size=PageSize(page_size_type='A4'), edge=PageEdge(page_edge_type='normal'),
                 pix_per_measure=None, color_mode=ColorMode.RGB):
        self.pix_per_measure = pix_per_measure or 10
        self.size = size
        self.edge = edge
        self.color_mode = color_mode
        print 'page_init width: %s, height: %s' % (self.size.width.v, self.size.height.v)

    def convert_edge_to_absolute(self, edge):
        d = dict(
            top=self.size.height * edge.top,
            bottom=self.size.height * edge.bottom,
            left=self.size.width * edge.left,
            right=self.size.width * edge.right,
        )
        return d

    def pix_of_measure(self, l):
        return self.pix_per_measure * l.inner_value

    @property
    def pix_info(self):
        info = dict(
            height_pix=self.pix_of_measure(self.size.height),
            width_pix=self.pix_of_measure(self.size.width)
        )
        return info


class DocPage(DocPageBase):
    def __init__(self, size=PageSize(page_size_type='A4'), edge=PageEdge(page_edge_type='normal'),
                 pix_per_measure=None, color_mode=ColorMode.RGB):
        super(DocPage, self).__init__(size=size, edge=edge, pix_per_measure=pix_per_measure, color_mode=color_mode)


if __name__ == '__main__':
    page = DocPage()
