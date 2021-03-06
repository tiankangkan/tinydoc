# -*- coding: UTF-8 -*-

"""
Desc: layout base.
Note:

---------------------------------------
# 2016/04/04   kangtian         created

"""

import copy
import os
import time
import json

from fpdf import FPDF

from k_util.str_op import to_unicode
from k_util.file_op import make_sure_file_dir_exists
from image.base import PosRect, PosPoint2D, Palette, ColorMode
from image.block import Block
from font.font_set import global_font_set
from font.font_char import FontChar
from layout_base import Area, LayoutLabel, LayoutAlign, LayoutSignal, Direction
from measure import Measure


DEFAULT_PIX_PER_MM = 15
DEFAULT_MEASURE = Measure(pix_per_mm=DEFAULT_PIX_PER_MM)


class LayoutSettingBase(object):
    def copy(self):
        return copy.deepcopy(self)


class LayoutTextSetting(LayoutSettingBase):
    char_spacing_cn = 0.15
    char_spacing_en = 0.1
    font_size_cn = 24
    font_size_en = 19
    line_spacing = 0.3
    line_direction = Direction(Direction.TO_BOTTOM)
    char_direction = Direction(Direction.TO_RIGHT)


class LayoutPageEdge(object):
    NORMAL = 'normal'
    NARROW = 'narrow'
    BROAD = 'broad'

    page_edge_type_mapping = {
        NORMAL: dict(top=0.0855, bottom=0.0855, left=0.151, right=0.151),
        NARROW: dict(top=0.0427, bottom=0.0427, left=0.0427, right=0.0427),
        BROAD: dict(top=0.0855, bottom=0.0855, left=0.241, right=0.241),
    }

    def __init__(self, page_edge_type=None):
        self.page_edge_type = page_edge_type or self.NORMAL
        d = self.page_edge_type_mapping[page_edge_type]
        top, bottom = d['top'], d['bottom']
        left, right = d['left'], d['right']
        self.top, self.bottom = top, bottom
        self.left, self.right = left, right
        self.top_v, self.right_v, self.bottom_v, self.left_v = 0, 0, 0, 0


class LayoutPageSize(object):
    A0, A1, A2, A3, A4, A5 = 'A0', 'A1', 'A2', 'A3', 'A4', 'A5'
    page_size_type_mapping = {
        'A0': dict(width=841, height=1189),
        'A1': dict(width=594, height=841),
        'A2': dict(width=420, height=594),
        'A3': dict(width=297, height=420),
        'A4': dict(width=210, height=297),
        'A5': dict(width=148, height=210),
    }

    def __init__(self, measure=None, page_size_type=None):
        self.m = measure or DEFAULT_MEASURE
        self.page_size_type = page_size_type or 'A4'
        d = self.page_size_type_mapping[page_size_type]
        self.width_mm, self.height_mm = d['width'], d['height']

        self.width = self.m.set_mm(self.width_mm).v
        self.height = self.m.set_mm(self.height_mm).v


class LayoutPageSetting(LayoutSettingBase):
    direction = Direction(Direction.TO_RIGHT)
    edge = LayoutPageEdge(page_edge_type=LayoutPageEdge.NORMAL)
    size = LayoutPageSize(page_size_type=LayoutPageSize.A4)


DEFAULT_TEXT_SETTING = LayoutTextSetting()
DEFAULT_PAGE_SETTING = LayoutPageSetting()


class LayoutBase(object):
    def __init__(self, owned_area=Area(), pix_per_mm=None):
        self.owned_area = owned_area
        self.free_area = copy.deepcopy(self.owned_area)
        self.sub_entry = []
        self.parent_entry = None
        self.mount_pos = PosPoint2D(x=0, y=0)
        self.label = LayoutLabel.LAYOUT
        self.bg_color = Palette.white
        self.fg_color = Palette.black
        self.block = None
        self.pix_per_mm = pix_per_mm or DEFAULT_PIX_PER_MM

    def font_obj(self, font_size):
        measure = Measure(pix_per_mm=self.pix_per_mm)
        measure.point = font_size
        return measure

    def append_entry(self, entry, ask_value=None):
        self.sub_entry.append(entry)
        entry.parent_entry = self
        entry.when_be_append()

    def sub_entry_iter(self):
        for entry in self.sub_entry:
            yield entry

    def earlier_entry(self, entry, label=None):
        entry_list = []
        if label:
            entry_list = self.get_sub_entry_list_with_labels(label)
        else:
            entry_list = self.sub_entry
        index = entry_list.index(entry)
        return entry_list[index - 1]

    def when_be_append(self, **args):
        pass

    def get_sub_entry_list_with_labels(self, label, res_list=None, find_recursive=False):
        res_list = res_list if res_list is not None else list()
        for entry in self.sub_entry_iter():
            if hasattr(label, '__iter__') and entry.label in label or entry.label == label:
                res_list.append(entry)
            if find_recursive:
                entry.get_sub_entry_list_with_labels(label, res_list=res_list, find_recursive=find_recursive)
        return res_list

    def layout(self):
        pass

    def redirection(self, x, y):
        pass

    def get_free_area(self):
        return self.free_area

    def add_free_area(self):
        pass

    def copy(self):
        return copy.deepcopy(self)

    def get_block(self):
        node = self
        while node and node.block is None:
            node = node.parent_entry
        block = node.block if node else None
        return block

    def __str__(self):
        s = 'owned_area: %s' % self.owned_area
        s += 'free_area: %s' % self.free_area
        return s


class LayoutLinearBase(LayoutBase):
    def __init__(self, owned_area=Area(), direction=Direction(Direction.TO_BOTTOM)):
        super(LayoutLinearBase, self).__init__(owned_area=owned_area)
        self.direction = direction
        self.owned_area_abs = None
        self.free_area_abs = None
        self.label = LayoutLabel.LAYOUT_LINEAR

    def __str__(self):
        return 'owned_area: %s, mount_pos: %s, owned_area_abs: %s' % (self.owned_area.rect, self.mount_pos, self.owned_area_abs)

    def get_free_area(self):
        return self.free_area

    def get_owned_area(self):
        return self.owned_area

    def get_used_area(self):
        used_rect = copy.deepcopy(self.owned_area.rect)
        used_area = Area(rect=used_rect)
        self.set_repr_measure_of_area(used_area, self.owned_repr - self.free_repr, direction=self.direction)
        return used_area

    @property
    def copy_owned_area(self):
        return self.get_owned_area().copy()

    @property
    def copy_free_area(self):
        return self.get_free_area().copy()

    @property
    def copy_used_area(self):
        return self.get_used_area().copy()

    @property
    def free_repr(self):
        return self.get_repr_measure_of_area(self.get_free_area())

    @property
    def used_repr(self):
        return self.get_repr_measure_of_area(self.get_used_area())

    @property
    def owned_repr(self):
        return self.get_repr_measure_of_area(self.get_owned_area())

    def get_repr_measure_of_area(self, area):
        direction = self.direction.direction
        # if not hasattr(area, 'rect') or area.rect is None:
        #     return 0
        if direction in (Direction.TO_BOTTOM, Direction.TO_TOP):
            r = area.rect.bottom - area.rect.top
        elif direction in (Direction.TO_RIGHT, Direction.TO_LEFT):
            r = area.rect.right - area.rect.left
        else:
            raise Exception('Can not accept direction: %s' % direction)
        return r

    def get_repr_fixed(self, area):
        rect = area.rect
        direction = self.direction.direction
        if direction in (Direction.TO_BOTTOM, Direction.TO_TOP):
            repr_value = rect.right - rect.left
        elif direction in (Direction.TO_RIGHT, Direction.TO_LEFT):
            repr_value = rect.bottom - rect.top
        else:
            raise Exception('Can not accept direction: %s' % direction)
        return repr_value

    def get_repr_variable(self, area):
        rect = area.rect
        direction = self.direction.direction
        if direction in (Direction.TO_RIGHT, Direction.TO_LEFT):
            repr_value = rect.right - rect.left
        elif direction in (Direction.TO_BOTTOM, Direction.TO_TOP):
            repr_value = rect.bottom - rect.top
        else:
            raise Exception('Can not accept direction: %s' % direction)
        return repr_value

    def set_repr_measure_of_area(self, area, value, direction):
        """
        :Note: Do not try to set used_area, used_area do not exist in self.
        :param area:
        :param value:
        :param direction:
        :return:
        """
        rect = area.rect
        if direction.direction == Direction.TO_BOTTOM:
            rect.bottom = rect.top + value
        elif direction.direction == Direction.TO_TOP:
            rect.top = rect.bottom - value
        elif direction.direction == Direction.TO_RIGHT:
            rect.right = rect.left + value
        elif direction.direction == Direction.TO_LEFT:
            rect.left = rect.right - value
        else:
            raise Exception('Can not accept direction: %s' % direction)
        return area

    def append_entry(self, entry, ask_value=None):
        if ask_value > self.free_repr:
            print 'Waring: OUT_OF_SPACE, ask: %s, free: %s' % (ask_value, self.free_repr)
            return LayoutSignal.OUT_OF_SPACE
        ask_value = ask_value if ask_value is not None else self.owned_repr
        # owned_area_temp = self.owned_area.copy()
        # self.set_repr_measure_of_area(owned_area_temp, ask_value, direction=self.direction)
        alloc_area = self.alloc_area(ask_value=ask_value)
        x = alloc_area.rect.left
        y = alloc_area.rect.top
        entry.mount_pos = PosPoint2D(x=x, y=y)
        entry.owned_area = alloc_area.copy()
        entry.owned_area.rect.translate(x=-x, y=-y)
        entry.free_area = copy.deepcopy(entry.owned_area)
        super(LayoutLinearBase, self).append_entry(entry=entry)
        return LayoutSignal.NORMAL

    def delta_area(self, area, delta_value, direction):
        rect = area.rect
        if direction.direction == Direction.TO_BOTTOM:
            rect.bottom += delta_value
        elif direction.direction == Direction.TO_TOP:
            rect.top -= delta_value
        elif direction.direction == Direction.TO_RIGHT:
            rect.right += delta_value
        elif direction.direction == Direction.TO_LEFT:
            rect.left -= delta_value
        else:
            raise Exception('Can not accept direction: %s' % direction)
        return area

    def offset(self, offset_value):
        if not self.parent_entry:
            raise Exception('Not find parent_entry, the process is not correct: %s' % self.direction)
        if self.parent_entry is not None:
            if self.direction.direction == Direction.TO_BOTTOM:
                self.mount_pos.y += offset_value
            elif self.direction.direction == Direction.TO_TOP:
                self.mount_pos.y -= offset_value
            elif self.direction.direction == Direction.TO_RIGHT:
                self.mount_pos.x += offset_value
            elif self.direction.direction == Direction.TO_LEFT:
                self.mount_pos.x -= offset_value
            else:
                raise Exception('Can not accept direction: %s' % self.direction)

    def alloc_area(self, ask_value):
        free_area = copy.deepcopy(self.get_free_area())
        free_repr = self.free_repr
        alloc_area = self.delta_area(free_area, -(free_repr - ask_value), self.direction)
        self.delta_free_area(delta_value=-ask_value)
        return alloc_area

    def exhaust_owned_area(self):
        self.delta_free_area(delta_value=-self.free_repr)

    def delta_free_area(self, delta_value, free_area=None):
        free_area = free_area or self.free_area
        self.delta_area(free_area, delta_value=delta_value, direction=-self.direction)

    def delta_owned_area(self, delta_value, owned_area=None):
        # TODO
        owned_area = owned_area or self.owned_area
        self.delta_area(owned_area, delta_value=delta_value, direction=self.direction)

    def fix_free_area_and_owned_area(self):
        rect_free = self.get_free_area().rect
        rect_owned = self.get_owned_area().rect
        rect_owned.make_include_another(rect_free)

    def convert_area_to_absolute(self, layout_node=None):
        layout_node = layout_node or self
        for entry in self.sub_entry_iter():
            p0 = entry.get_mount_to_layout_node(layout_node=layout_node)
            entry.owned_area_abs = entry.get_owned_area().copy()
            entry.owned_area_abs.rect.translate(x=p0.x, y=p0.y)
            entry.free_area_abs = entry.get_free_area().copy()
            entry.free_area_abs.rect.translate(x=p0.x, y=p0.y)
            entry.convert_area_to_absolute(layout_node)

    def get_mount_to_layout_node(self, layout_node=None):
        mount_pos = copy.deepcopy(self.mount_pos)
        entry_tmp = self
        while True:
            if entry_tmp is not layout_node:
                entry_tmp = entry_tmp.parent_entry
                mount_pos += entry_tmp.mount_pos
            else:
                break
        return mount_pos

    def refresh(self):
        entry_num = len(self.sub_entry)
        free_value = 0
        for i in range(entry_num):
            entry_now = self.sub_entry[i]
            if entry_now.direction in (self.direction, -self.direction):
                free_area_repr = entry_now.refresh()
            else:
                free_area_repr = 0
            free_value += free_area_repr
            for after_entry in self.sub_entry[i + 1:]:
                after_entry.offset(-free_area_repr)
        free_area_repr = self.free_repr
        self.set_repr_measure_of_area(self.free_area, 0, -self.direction)
        free_value += free_area_repr
        self.delta_owned_area(-free_value)
        self.fix_free_area_and_owned_area()
        return free_value


class LayoutLinearFree(LayoutLinearBase):
    def __init__(self, owned_area=Area(), direction=Direction(Direction.TO_BOTTOM)):
        super(LayoutLinearFree, self).__init__(owned_area=owned_area, direction=direction)
        self.exhaust_owned_area()

    def append_entry_free(self, entry, mount_pos):
        super(LayoutLinearFree, self).append_entry(entry)
        entry.mount_pos = mount_pos


class LayoutSpacing(LayoutLinearBase):
    def __init__(self, owned_area=Area(), direction=Direction(Direction.TO_BOTTOM)):
        super(LayoutSpacing, self).__init__(owned_area=owned_area, direction=direction)
        self.label = LayoutLabel.SPACING

    def when_be_append(self, **args):
        self.exhaust_owned_area()


# class LayoutLinearVerticalRel(LayoutLinearBase):
#     def __init__(self, owned_area=Area(), direction=Direction(Direction.TO_BOTTOM)):
#         super(LayoutLinearVerticalRel, self).__init__(owned_area=owned_area, direction=direction)
# 
# 
# class LayoutLinearHorizontalRel(LayoutLinearBase):
#     def __init__(self, owned_area=Area(), direction=Direction(Direction.TO_RIGHT)):
#         super(LayoutLinearHorizontalRel, self).__init__(owned_area=owned_area, direction=direction)


class LayoutCharAtom(LayoutLinearBase):
    def __init__(self, font_ch, owned_area=Area(), direction=Direction(Direction.TO_BOTTOM)):
        super(LayoutCharAtom, self).__init__(owned_area=owned_area, direction=direction)
        self.font_ch = font_ch
        self.label = LayoutLabel.CHAR_ATOM


class LayoutChar(LayoutLinearBase):
    def __init__(self, font_ch, font_size, owned_area=Area(), direction=Direction(Direction.TO_LEFT)):
        super(LayoutChar, self).__init__(owned_area=owned_area, direction=direction)
        self.font_ch = font_ch
        self.font_size = font_size
        self.label = LayoutLabel.CHAR

    def when_be_append(self, **args):
        self.set_with_ch(self.font_ch)

    def set_with_ch(self, font_ch):
        scale = self.font_obj(font_size=self.font_size).v / (font_ch.ch_width + 0.00001)
        valid_rect = font_ch.get_valid_rect(direction=self.parent_entry.direction)
        if self.direction.is_vertical:
            line_height = self.owned_area.rect.height
            padding_top = int((line_height - valid_rect.height * scale) / 2)
            char_height = valid_rect.height * scale
        elif self.direction.is_horizontal:
            line_height = self.owned_area.rect.width
            padding_top = int((line_height - valid_rect.width * scale) / 2)
            char_height = valid_rect.width * scale
        else:
            raise Exception('Can not accept direction: %s' % self.direction)
        # line_height, padding_top, char_height = line_height * scale, padding_top * scale, char_height * scale
        # print 'line_height: %s, padding_top: %s, char_height: %s' % (line_height, padding_top, char_height)
        padding_bottom = line_height - padding_top - char_height
        self.append_entry(LayoutSpacing(), ask_value=padding_top)  # 字符上面的空白间距
        ch_atom = LayoutCharAtom(font_ch)
        self.append_entry(ch_atom, ask_value=char_height)  # 字符实体
        self.append_entry(LayoutSpacing(), ask_value=padding_bottom)  # 字符下边的空白间距


class LayoutCharSpacing(LayoutLinearBase):
    def __init__(self, owned_area=Area(), direction=Direction(Direction.TO_BOTTOM)):
        super(LayoutCharSpacing, self).__init__(owned_area=owned_area, direction=direction)
        self.label = LayoutLabel.CHAR_SPACING


class LayoutTextLineSpacing(LayoutLinearBase):
    def __init__(self, owned_area=Area(), direction=Direction(Direction.TO_BOTTOM)):
        super(LayoutTextLineSpacing, self).__init__(owned_area=owned_area, direction=direction)
        self.label = LayoutLabel.TEXT_LINE_SPACING


class LayoutTextLineBase(LayoutLinearBase):
    def __init__(self, char_spacing_cn=None, char_spacing_en=None, owned_area=Area(),
                 direction=Direction(Direction.TO_RIGHT), font_size=None):
        super(LayoutTextLineBase, self).__init__(owned_area=owned_area, direction=direction)
        self.char_spacing_cn = char_spacing_cn or DEFAULT_TEXT_SETTING.char_spacing_cn
        self.char_spacing_en = char_spacing_en or DEFAULT_TEXT_SETTING.char_spacing_en
        self.label = LayoutLabel.TEXT_LINE
        self.font_size = font_size or 12

    # def when_be_append(self, **args):
    #     self.exhaust_owned_area()

    def append_char(self, ch, font_size=None):
        font_size = font_size or self.font_size
        font_ch = global_font_set.get_char(ch)
        valid_rect = font_ch.get_valid_rect(direction=self.direction)
        # insert char

        scale = self.font_obj(font_size=font_size).v / (font_ch.ch_width + 0.0001)
        if self.direction.is_horizontal:
            src_width = valid_rect.right - valid_rect.left
        elif self.direction.is_vertical:
            src_width = valid_rect.bottom - valid_rect.top
        else:
            raise Exception('Can not accept direction: %s' % self.direction)
        ask_value = scale * src_width
        # print 'char_width: %s, font_ch.ch_width: %s' % (ask_value, font_ch.ch_width)
        layout_ch = LayoutChar(font_ch=font_ch, font_size=self.font_size, direction=self.direction.add())
        signal = self.append_entry(layout_ch, ask_value=ask_value)
        if signal == LayoutSignal.OUT_OF_SPACE:
            return signal  # out of space.
        layout_ch.exhaust_owned_area()

        # insert spacing
        layout_spacing = LayoutCharSpacing()
        ch_spacing = self.get_ch_spacing(font_ch)
        signal = self.append_entry(layout_spacing, ask_value=ch_spacing)
        if signal == LayoutSignal.OUT_OF_SPACE:
            pass  # out of space, but ignore.
        else:
            layout_spacing.exhaust_owned_area()
        return LayoutSignal.NORMAL

    def get_ch_spacing(self, font_ch, font_size=None):
        font_size = font_size or self.font_size
        # valid_rect = font_ch.get_valid_rect(direction=self.direction)
        # if self.direction.is_horizontal:
        #     length = valid_rect.width
        # elif self.direction.is_vertical:
        #     length = valid_rect.height
        # else:
        #     raise Exception('Can not accept direction: %s' % self.direction)
        length = self.font_obj(font_size=font_size).v
        if font_ch.is_en_char():
            ch_spacing = int(self.char_spacing_en * length)
        else:
            ch_spacing = int(self.char_spacing_cn * length)
        return int(ch_spacing)

    def create_layout_of_text(self, text):
        text = to_unicode(text)
        for ch in text:
            self.append_char(ch)

    def render(self, root=None):
        # self.convert_area_to_absolute()
        block = self.get_block()
        ch_atom_list = self.get_sub_entry_list_with_labels(LayoutLabel.CHAR_ATOM, find_recursive=True)
        for entry in ch_atom_list:
            ch_atom = entry
            font_ch = ch_atom.font_ch
            valid_rect = font_ch.get_valid_rect(direction=self.direction)
            block_ch = font_ch.block
            block_ch = block_ch.cut_with_rect(valid_rect)
            dst_rect = ch_atom.owned_area_abs.rect.copy()
            # print 'dst_rect: %s' % dst_rect
            block.paste(block_ch, top=dst_rect.top, left=dst_rect.left, right=dst_rect.right)


class LayoutTextLine(LayoutTextLineBase):
    def __init__(self, direction, char_spacing_cn=None, char_spacing_en=None,
                 owned_area=Area(), font_size=None):
        super(LayoutTextLine, self).__init__(char_spacing_cn=char_spacing_cn, char_spacing_en=char_spacing_en,
                                             owned_area=owned_area, direction=direction, font_size=font_size)


class LayoutTextBase(LayoutLinearBase):
    def __init__(self, owned_area=None, setting=None, font_size_cn=None, font_size_en=None, line_spacing=None,
                 char_spacing_cn=None, char_spacing_en=None, line_direction=None, char_direction=None):
        setting = setting or DEFAULT_TEXT_SETTING
        self.line_spacing = line_spacing or setting.line_spacing
        self.char_spacing_cn = char_spacing_cn or setting.char_spacing_cn
        self.char_spacing_en = char_spacing_en or setting.char_spacing_en
        self.font_size_cn = font_size_cn or setting.font_size_cn
        self.font_size_en = font_size_en or setting.font_size_en
        self.line_direction = line_direction or setting.line_direction
        self.char_direction = char_direction or setting.char_direction
        direction = self.line_direction
        owned_area = owned_area or Area()
        super(LayoutTextBase, self).__init__(owned_area=owned_area, direction=direction)
        self.label = LayoutLabel.TEXT

    @property
    def font_size(self):
        return self.font_size_cn

    def get_line_spacing(self, line_height):
        return int(self.line_spacing * line_height)

    def get_cur_line(self, new_line_height):
        lines_entry = self.get_sub_entry_list_with_labels(LayoutLabel.TEXT_LINE)
        line_index = len(lines_entry) - 1
        if line_index < 0:
            signal = self.append_line(ask_value=new_line_height)
            if signal == LayoutSignal.OUT_OF_SPACE:
                return signal  # out of space.
            lines_entry = self.get_sub_entry_list_with_labels(LayoutLabel.TEXT_LINE)
        return lines_entry[-1]

    def append_line(self, ask_value=None):
        if self.direction.parallel_with(self.char_direction):
            raise ValueError('char_direction MUST be vertically with line_direction')
        layout_line = LayoutTextLine(direction=self.char_direction, char_spacing_cn=self.char_spacing_cn,
                                     char_spacing_en=self.char_spacing_en, font_size=self.font_size)
        signal = self.append_entry(layout_line, ask_value=ask_value)
        if signal == LayoutSignal.OUT_OF_SPACE:
            return signal  # out of space.
        layout_line_spacing = LayoutTextLineSpacing(direction=self.direction)
        line_spacing = self.get_line_spacing(line_height=ask_value)
        signal = self.append_entry(layout_line_spacing, ask_value=line_spacing)
        if signal == LayoutSignal.OUT_OF_SPACE:
            pass  # out of space, ignore.
        return LayoutSignal.NORMAL

    def append_text(self, text):
        print 'LayoutTextBase:append_text: %s' % text
        line_height = self.get_line_height()
        cur_line = self.get_cur_line(new_line_height=line_height)
        text = to_unicode(text)
        for index in range(len(text)):
            ch = text[index]
            if ch == '\n':
                line_signal = self.append_line(ask_value=line_height)
                if line_signal == LayoutSignal.OUT_OF_SPACE:
                    return line_signal, text[index:]
                cur_line = self.get_cur_line(new_line_height=line_height)
                continue
            signal = cur_line.append_char(ch)
            # 一直分配行,直到可以放下 char. 当没有足够的行时, 返回 LayoutSignal.OUT_OF_SPACE
            while signal == LayoutSignal.OUT_OF_SPACE:
                print 'LayoutSignal.OUT_OF_SPACE'
                line_signal = self.append_line(ask_value=line_height)
                if line_signal == LayoutSignal.OUT_OF_SPACE:
                    return line_signal, text[index:]
                cur_line = self.get_cur_line(new_line_height=line_height)
                signal = cur_line.append_char(ch)
        self.parent_entry.delta_free_area(self.free_repr)
        print 'self.free_repr: %s' % self.free_repr
        return LayoutSignal.NORMAL, ''

    def get_line_height(self):
        font_size = self.font_size
        pix_num = self.font_obj(font_size=font_size,).v
        return pix_num

    def render(self, root=None):
        if not root:
            self.convert_area_to_absolute()
        for entry in self.get_sub_entry_list_with_labels(LayoutLabel.TEXT_LINE, find_recursive=True):
            entry.render(root=root)


class LayoutText(LayoutTextBase):
    def __init__(self, owned_area=None, setting=None, font_size_cn=None, font_size_en=None, line_spacing=None,
                 char_spacing_cn=None, char_spacing_en=None, line_direction=None, char_direction=None):
        super(LayoutText, self).__init__(owned_area=owned_area, setting=setting, font_size_cn=font_size_cn,
                                         font_size_en=font_size_en, line_spacing=line_spacing,
                                         char_spacing_cn=char_spacing_cn, char_spacing_en=char_spacing_en,
                                         line_direction=line_direction, char_direction=char_direction)


class SegmentSpacing(LayoutLinearBase):
    def __init__(self, owned_area=Area(), direction=Direction(Direction.TO_BOTTOM)):
        super(SegmentSpacing, self).__init__(owned_area=owned_area, direction=direction)
        self.label = LayoutLabel.SEGMENT_SPACING


class LayoutWebPage(LayoutLinearBase):
    def __init__(self, layout_page=None, owned_area=None, setting=None, direction=None, edge=None,
                 size=None, index=None, color_mode=None, bg_color=None):
        if layout_page:
            direction = direction or layout_page.direction
            p = layout_page
            width = self.get_repr_fixed(self.owned_area) - (p.edge.right_v + p.edge.left_v)
            height = self.get_repr_variable(self.owned_area) - (p.edge.top_v + p.edge.bottom_v)
            owned_area = owned_area or Area(PosRect(top=0, left=0, right=width, bottom=height))
            index = index or p.index
            color_mode = color_mode or p.color_mode
            bg_color = bg_color or p.bg_color
            self.parent_entry = layout_page
        self.color_mode = color_mode or ColorMode.RGB
        self.bg_color = bg_color or Palette.white
        self.index = index or 0
        owned_area = owned_area or Area()
        direction = direction or DEFAULT_PAGE_SETTING.direction
        super(LayoutWebPage, self).__init__(owned_area=owned_area, direction=direction)

    def separate(self, ask_value):
        part_list = list()
        while self.owned_repr > ask_value:
            part = self.cut_head(ask_value)
            part_list.append(part)
        return part_list

    def cut_head(self, ask_value):
        head_web_page = self
        head_web_page.set_repr_measure_of_area(self.get_owned_area(), ask_value, self.direction)
        return head_web_page

    def __str__(self):
        return 'Page [%s], Width: %s' % (self.index, self.owned_area.rect.width)


class LayoutPageBase(LayoutLinearBase):
    def __init__(self, owned_area=Area(), setting=None, edge=None, size=None, index=None, direction=None, color_mode=None, bg_color=None):
        setting = setting or DEFAULT_PAGE_SETTING
        direction = direction or setting.direction
        self.edge = edge or setting.edge
        self.size = size or setting.size
        self.index = index or 0
        self.edge.top_v = int(self.edge.top * self.size.height)
        self.edge.right_v = int(self.edge.right * self.size.width)
        self.edge.bottom_v = int(self.edge.bottom * self.size.height)
        self.edge.left_v = int(self.edge.left * self.size.width)
        self.color_mode = color_mode or ColorMode.RGB
        self.bg_color = bg_color or Palette.white
        self.page_body = None
        self.pix_per_mm = 25
        self.label = LayoutLabel.PAGE
        owned_area = Area(rect=PosRect(top=0, bottom=self.size.height, left=0, right=self.size.width))
        super(LayoutPageBase, self).__init__(owned_area=owned_area, direction=direction)
        self.init()

    def init(self):
        spacing_left, spacing_right = self.edge.left_v, self.edge.right_v
        super(LayoutPageBase, self).append_entry(LayoutSpacing(), ask_value=spacing_left)
        center_direction = self.direction.add()
        center_layout = LayoutLinearBase(direction=center_direction)
        center_repr = self.get_repr_variable(self.get_owned_area()) - (spacing_left+spacing_right)    # TODO
        super(LayoutPageBase, self).append_entry(center_layout, ask_value=center_repr)
        super(LayoutPageBase, self).append_entry(LayoutSpacing(), ask_value=spacing_right)

        print 'center_layout: %s' % center_layout

        spacing_top, spacing_bottom = self.edge.top_v, self.edge.bottom_v
        center_layout.append_entry(LayoutSpacing(), ask_value=spacing_top)
        page_body = LayoutLinearBase(direction=center_layout.direction)
        page_body_repr = center_layout.get_repr_variable(self.get_owned_area()) - (spacing_top + spacing_bottom)    # TODO
        center_layout.append_entry(page_body, ask_value=page_body_repr)
        center_layout.append_entry(LayoutSpacing(), ask_value=spacing_bottom)
        self.page_body = page_body
        print 'page_body: %s' % page_body

    def render(self, root=None):
        root = root or self
        block = self.get_block()
        self.convert_area_to_absolute()

        for entry in self.get_sub_entry_list_with_labels(LayoutLabel.TEXT, find_recursive=True):
            entry.render(root=root)

        # # 骨架
        # for entry in self.get_sub_entry_list_with_labels(LayoutLabel().frame_label_list, find_recursive=True):
        #     block.draw_rect(entry.owned_area_abs.rect, width=5, color=Palette.blue, draw_inside=True)

        # for entry in self.get_sub_entry_list_with_labels(LayoutLabel().spacing_label_list, find_recursive=True):
        #     block.draw_rect(entry.owned_area_abs.rect, width=3, color=Palette.black, draw_inside=True)
        #
        # for entry in self.get_sub_entry_list_with_labels(LayoutLabel().atom_label_list, find_recursive=True):
        #     block.draw_rect(entry.owned_area_abs.rect, width=2, color=Palette.red, draw_inside=True)

    def append_entry(self, entry, ask_value=None):
        return self.page_body.append_entry(entry=entry, ask_value=ask_value)

    def __str__(self):
        return 'Page [%s], Size(%s, %s), Edge(%s, %s, %s, %s)' % (self.index, self.size.width, self.size.height,
                                                                  self.edge.top_v, self.edge.right_v,
                                                                  self.edge.bottom_v, self.edge.left_v)


class LayoutDocumentBase(object):
    def __init__(self, doc_identify='MyDoc', session_dir='', page_edge=None, page_size=None, color_mode=None, bg_color=None):
        self.label = LayoutLabel.DOCUMENT
        self.doc_identify = doc_identify
        self.session_dir = session_dir
        self.page_edge = page_edge or DEFAULT_PAGE_SETTING.edge
        self.page_size = page_size or DEFAULT_PAGE_SETTING.size
        self.color_mode = color_mode
        self.bg_color = bg_color

        self.doc_info = dict()
        self.page_list = list()
        self.add_page()

    def add_page(self):
        new_page = LayoutPageBase(edge=self.page_edge, size=self.page_size, color_mode=self.color_mode, bg_color=self.bg_color)
        self.page_list.append(new_page)

    @property
    def cur_page(self):
        return self.page_list[-1]

    def page_iter(self):
        for page in self.page_list:
            yield page

    def append_text(self, text, line_direction=None):
        print 'append_text: %s' % text
        layout_text = LayoutText(line_direction=line_direction)
        self.cur_page.append_entry(layout_text)
        signal, left_text = layout_text.append_text(text)
        if signal == LayoutSignal.OUT_OF_SPACE:
            print 'left_text: %s' % left_text
            self.add_page()
            self.append_text(left_text)
        return LayoutSignal.NORMAL, ''

    def render(self, session_dir=None, to_image=None, to_pdf=None):
        render = RenderDocumentBase(layout=self)
        render.render(to_image=to_image, to_pdf=to_pdf)

    def get_pdf_path(self):
        pdf_path = os.path.join(self.session_dir, '%s.pdf' % self.doc_identify)
        make_sure_file_dir_exists(pdf_path)
        return pdf_path

    def get_page_path(self, index):
        page_path = os.path.join(self.session_dir, '%s_%s.jpg' % (self.doc_identify, index))
        make_sure_file_dir_exists(page_path)
        return page_path

    def get_doc_info_path(self):
        doc_info_path = os.path.join(self.session_dir, '%s.info' % self.doc_identify)
        make_sure_file_dir_exists(doc_info_path)
        return doc_info_path


class RenderBase(object):
    def __init__(self, layout):
        self.layout = layout
        self.block = Block()

    def render(self):
        pass


class RenderPageBase(RenderBase):
    def __init__(self, layout):
        super(RenderPageBase, self).__init__(layout=layout)

    def ready(self):
        height = self.layout.size.height
        width = self.layout.size.width
        color_mode = self.layout.color_mode
        bg_color = self.layout.bg_color
        self.block = Block(width=width, height=height, color_mode=color_mode, color=bg_color)
        self.layout.block = self.block
        return self

    def render(self):
        self.ready()
        self.layout.render()

    def to_image_file(self, file_path):
        make_sure_file_dir_exists(file_path)
        self.block.to_file(file_path)


class RenderDocumentBase(RenderBase):
    def __init__(self, layout):
        super(RenderDocumentBase, self).__init__(layout=layout)
        self.page_list = list()
        self.image_list = []
        self.pdf_path = ''
        self.doc_info = dict()

    def render(self, to_image=None, to_pdf=None):
        to_pdf = to_pdf or True
        to_image = to_image or True
        to_image = True if to_pdf else to_image

        index = 1
        for page in self.layout.page_iter():
            render_page = RenderPageBase(layout=page)
            render_page.render()
            if to_image:
                image_path = self.layout.get_page_path(index=index)
                render_page.to_image_file(image_path)
                self.image_list.append(image_path)
                print 'Output Image: %s' % image_path
            self.page_list.append(render_page)
            index += 1
        if to_pdf:
            self.gen_pdf_from_image_list(self.image_list)

        self.doc_info = dict(
            pdf_path=self.pdf_path,
            image_list=self.image_list
        )
        with open(self.layout.get_doc_info_path(), 'wb') as fp:
            json.dump(self.doc_info, fp, indent=4)
        self.layout.doc_info = self.doc_info

    def gen_pdf_from_image_list(self, image_list):
        page_size = self.layout.page_size
        page_type = page_size.page_size_type
        page_width = page_size.width_mm
        pdf = FPDF(orientation='P', unit='mm', format=page_type)
        for image_path in image_list:
            pdf.add_page()
            pdf.image(image_path, 0, 0, page_width)
        self.pdf_path = self.layout.get_pdf_path()
        pdf.output(name=self.pdf_path)
        print 'Output PDF: %s' % self.pdf_path


def test_of_layout_base():
    page_area = Area(rect=PosRect(top=0, left=0, bottom=3000, right=2000))
    page = LayoutLinearBase(owned_area=page_area)
    text_first = LayoutLinearBase()
    text_second = LayoutLinearBase()
    page.append_entry(text_first, ask_value=1200)
    page.append_entry(text_second, ask_value=400)
    text_first.delta_free_area(-300)
    text_second.delta_free_area(-280)
    print 'page.owned_area: ', page.owned_area.rect
    print 'page.free_area: ', page.free_area.rect
    print 'text_first.owned_area: ', text_first.owned_area.rect
    print 'text_first.free_area: ', text_first.free_area.rect
    print 'text_second.owned_area: ', text_second.owned_area.rect
    print 'text_second.free_area: ', text_second.free_area.rect

    print '\n\n'

    page.refresh()
    page.convert_area_to_absolute()
    print 'page.owned_area: ', page.owned_area.rect
    print 'page.free_area: ', page.free_area.rect
    print 'text_first.owned_area: ', text_first.owned_area.rect
    print 'text_first.free_area: ', text_first.free_area.rect.to_points()
    print 'text_second.owned_area: ', text_second.owned_area_abs.rect
    print 'text_second.free_area: ', text_second.free_area_abs.rect
    print 'ok'


def test_of_layout_text_line():
    text_line = LayoutTextLine(direction=Direction(Direction.TO_LEFT), owned_area=owned_area)
    text_line.create_layout_of_text('hi,我们都是好孩子')
    text_line.render()


def test_of_layout_text():
    t_start = time.time()
    page = LayoutPageBase()
    # page.convert_area_to_absolute()
    print page
    print page.page_body
    # webpage = LayoutWebPage(layout_page=page)
    r = RenderPageBase(layout=page)

    # print r
    r.ready()

    text = """在开罗以南700千米处的尼罗河东岸。 遗址占据当时底比斯东城的北半部。通过斯芬克斯（见狮身人面像）大道与南面1千米的卢克索相接，那里另有一座阿蒙神庙。由于中王国和新王国各朝都是从底比斯起家而统治全国的，底比斯的地方神阿蒙神被当做王权的保护神，成为埃及众神中最重要的一位。这里的阿蒙神庙也成"""

    layout_text = LayoutText(line_direction=Direction(Direction.TO_BOTTOM))
    page.append_entry(layout_text)

    print 'layout_text.direction.direction', layout_text.direction.direction
    layout_text.append_text(text)

    layout_text.append_text('Hello, world')

    page.render()
    r.to_image_file('page.jpg')
    os.system('open page.jpg')


def test_of_layout_document():
    t_start = time.time()
    doc = LayoutDocumentBase()
    text_1 = """在开罗以南700千米处的尼罗河东岸。 遗址占据当时底比斯东城的北半部。通过斯芬克斯（见狮身人面像）大道与南面1千米的卢克索相接，那里另有一座阿蒙神庙。由于中王国和新王国各朝都是从底比斯起家而统治全国的，底比斯的地方神阿蒙神被当做王权的保护神，成为埃及众神中最重要的一位。这里的阿蒙神庙也成"""
    text_1 += '\n'*40
    text_2 = '不喜欢蓝色的青年不是好青年'
    doc.append_text(text_1, line_direction=Direction(Direction.TO_BOTTOM))
    doc.append_text(text_2)
    doc.append_text('Hello world')
    doc.render()
    # render = RenderDocumentBase(layout=doc)
    # render.render()


if __name__ == '__main__':
    # test_of_layout_text()
    test_of_layout_document()


