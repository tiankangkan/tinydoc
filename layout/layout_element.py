# -*- coding: UTF-8 -*-

"""
Desc: layout base.
Note:

---------------------------------------
# 2016/04/04   kangtian         created

"""

import copy

from k_util.str_op import to_unicode
from image.base import PosRect, PosPoint2D, Palette
from image.block import Block
from font.font_set import global_font_set
from font.font_char import FontChar
from layout_base import Area, LayoutLabel, LayoutAlign, LayoutSignal, Direction


class LayoutSetting(object):
    char_spacing_cn = 0.2
    char_spacing_en = 0.1
    line_spacing = 0.3

default_setting = LayoutSetting()


class LayoutBase(object):
    def __init__(self, owned_area=Area()):
        self.owned_area = owned_area
        self.free_area = copy.deepcopy(self.owned_area)
        self.sub_entry = []
        self.parent_entry = None
        self.mount_pos = PosPoint2D(x=0, y=0)
        self.label = LayoutLabel.LAYOUT

    def append_entry(self, entry, ask_value=None):
        self.sub_entry.append(entry)
        entry.parent_entry = self
        entry.when_be_append()

    def sub_entry_iter(self):
        for entry in self.sub_entry:
            yield entry

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
        print type(entry)
        print 'entry: %s, %s' % (entry.owned_area, entry.free_area)
        print 'append-mount_pos=%s alloc_area=%s' % (entry.mount_pos, alloc_area)
        super(LayoutLinearBase, self).append_entry(entry=entry)
        return LayoutSignal.NORMAL
        # print 'pos=', self.mount_pos

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
        alloc_area = self.delta_area(free_area, -(free_repr-ask_value), self.direction)
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
            print 'translate=', p0
            entry.owned_area_abs = entry.get_owned_area().copy()
            entry.owned_area_abs.rect.translate(x=p0.x, y=p0.y)
            print 'owned_area_abs=', entry.owned_area_abs.rect
            entry.free_area_abs = entry.get_free_area().copy()
            entry.free_area_abs.rect.translate(x=p0.x, y=p0.y)
            entry.convert_area_to_absolute(layout_node)
            print type(entry)

    def get_mount_to_layout_node(self, layout_node=None):
        mount_pos = copy.deepcopy(self.mount_pos)
        entry_tmp = self
        while True:
            if entry_tmp is not layout_node:
                entry_tmp = entry_tmp.parent_entry
                mount_pos += entry_tmp.mount_pos
                # if entry_tmp.direction.direction in (Direction.TO_BOTTOM, Direction.TO_RIGHT):
                #     mount_pos += entry_tmp.mount_pos
                # elif entry_tmp.direction.direction in (Direction.TO_TOP, Direction.TO_LEFT):
                #     mount_pos -= entry_tmp.mount_pos
                # else:
                #     raise Exception('Can not accept direction: %s' % self.direction)
                # # print 'abs-mount_pos=', mount_pos
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
            for after_entry in self.sub_entry[i+1:]:
                after_entry.offset(-free_area_repr)
        free_area_repr = self.free_repr
        self.set_repr_measure_of_area(self.free_area, 0, -self.direction)
        free_value += free_area_repr
        self.delta_owned_area(-free_value)
        self.fix_free_area_and_owned_area()
        return free_value

# class LayoutLinearVerticalAbs(LayoutLinearBase):
#     def __init__(self, owned_area=Area(), direction=Direction(Direction.TO_BOTTOM)):
#         super(LayoutLinearVerticalAbs, self).__init__(owned_area=owned_area, direction=direction)
#
#     def append_entry(self, entry, ask_value=None):
#         ask_value = ask_value if ask_value is not None else self.owned_repr
#         alloc_area = self.alloc_area(ask_value)
#         entry.owned_area = alloc_area
#         entry.free_area = copy.deepcopy(entry.owned_area)
#         super(LayoutLinearVerticalAbs, self).append(entry=entry)
#
#     def offset(self, offset_value):
#         if self.direction.direction == Direction.TO_BOTTOM:
#             self.owned_area.rect.translate(0, offset_value)
#         elif self.direction.direction == Direction.TO_TOP:
#             self.owned_area.rect.translate(0, -offset_value)
#         for entry in self.sub_entry:
#             entry.offset(offset_value)
#
#     def refresh(self):
#         entry_num = len(self.sub_entry)
#         free_value = 0
#         for i in range(entry_num):
#             entry_now = self.sub_entry[i]
#             if entry_now.direction in (self.direction, -self.direction):
#                 free_area_repr = entry_now.refresh()
#             else:
#                 free_area_repr = 0
#             free_value += free_area_repr
#             for after_entry in self.sub_entry[i+1:]:
#                 after_entry.offset(-free_area_repr)
#         free_area_repr = self.free_repr
#         self.set_repr_measure_of_area(self.free_area, 0, -self.direction)
#         free_value += free_area_repr
#         self.delta_owned_area(-free_value)
#         self.fix_free_area_and_owned_area()
#         return free_value
#
#     def fix_free_area_and_owned_area(self):
#         rect_free = self.free_area.rect
#         rect_owned = self.owned_area.rect
#         rect_owned.make_include_another(rect_free)


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
    def __init__(self, font_ch, owned_area=Area(), direction=Direction(Direction.TO_LEFT)):
        super(LayoutChar, self).__init__(owned_area=owned_area, direction=direction)
        self.font_ch = font_ch
        self.label = LayoutLabel.CHAR

    def when_be_append(self, **args):
        self.set_with_ch(self.font_ch)

    def set_with_ch(self, font_ch):
        valid_rect = font_ch.get_valid_rect(direction=self.parent_entry.direction)
        if self.direction.is_vertical:
            line_height = self.owned_area.rect.height
            padding_top = int((line_height - valid_rect.height) / 2)
            char_height = valid_rect.bottom - valid_rect.top

        elif self.direction.is_horizontal:
            line_height = self.owned_area.rect.width
            padding_top = int((line_height - valid_rect.width) / 2)
            char_height = valid_rect.width
        else:
            raise Exception('Can not accept direction: %s' % self.direction)
        padding_bottom = line_height - padding_top - char_height
        self.append_entry(LayoutSpacing(), ask_value=padding_top)    # 字符上面的空白间距
        ch_atom = LayoutCharAtom(font_ch)
        self.append_entry(ch_atom, ask_value=char_height)    # 字符实体
        print 'set_with_ch', ch_atom.mount_pos
        self.append_entry(LayoutSpacing(), ask_value=padding_bottom)    # 字符下边的空白间距
        
    # def do_layout(self):
    #     font_ch = self.font_ch
    #     valid_rect = font_ch.get_valid_rect()
    #     margin_top = int((self.line_height - valid_rect.height) / 2)
    #     # block_ch = font_ch.block
    #     # block_ch = block_ch.cut_with_rect(valid_rect)
    #     dst_rect = self.owned_area_abs.rect.copy()
    #     block.paste(block_ch, top=int(dst_rect.top+margin_top), left=int(dst_rect.left))
    #     block.draw_rect(self.owned_area_abs.rect, width=3)


class LayoutCharSpacing(LayoutLinearBase):
    def __init__(self, owned_area=Area(), direction=Direction(Direction.TO_BOTTOM)):
        super(LayoutCharSpacing, self).__init__(owned_area=owned_area, direction=direction)
        self.label = LayoutLabel.CHAR_SPACING


class LayoutTextLineSpacing(LayoutLinearBase):
    def __init__(self, owned_area=Area(), direction=Direction(Direction.TO_BOTTOM)):
        super(LayoutTextLineSpacing, self).__init__(owned_area=owned_area, direction=direction)
        self.label = LayoutLabel.TEXT_LINE_SPACING


class LayoutTextLineBase(LayoutLinearBase):
    def __init__(self, char_spacing_cn=None, char_spacing_en=None, owned_area=Area(), direction=Direction(Direction.TO_RIGHT)):
        super(LayoutTextLineBase, self).__init__(owned_area=owned_area, direction=direction)
        self.char_spacing_cn = char_spacing_cn or default_setting.char_spacing_cn
        self.char_spacing_en = char_spacing_en or default_setting.char_spacing_en
        self.label = LayoutLabel.TEXT_LINE

    # def when_be_append(self, **args):
    #     self.exhaust_owned_area()

    def append_char(self, ch):
        font_ch = global_font_set.get_char(ch)
        valid_rect = font_ch.get_valid_rect(direction=self.direction)
        # insert char
        if self.direction.is_horizontal:
            ask_value = valid_rect.right - valid_rect.left
        elif self.direction.is_vertical:
            ask_value = valid_rect.bottom - valid_rect.top
        else:
            raise Exception('Can not accept direction: %s' % self.direction)
        layout_ch = LayoutChar(font_ch=font_ch)
        signal = self.append_entry(layout_ch, ask_value=ask_value)
        if signal == LayoutSignal.OUT_OF_SPACE:
            return signal    # out of space.
        layout_ch.exhaust_owned_area()

        # insert spacing
        layout_spacing = LayoutCharSpacing()
        ch_spacing = self.get_ch_spacing(font_ch)
        signal = self.append_entry(layout_spacing, ask_value=ch_spacing)
        if signal == LayoutSignal.OUT_OF_SPACE:
            pass    # out of space, but ignore.
        else:
            layout_spacing.exhaust_owned_area()
        return LayoutSignal.NORMAL

    def get_ch_spacing(self, font_ch):
        valid_rect = font_ch.get_valid_rect(direction=self.direction)
        if self.direction.is_horizontal:
            length = valid_rect.width
        elif self.direction.is_vertical:
            length = valid_rect.height
        else:
            raise Exception('Can not accept direction: %s' % self.direction)
        if font_ch.is_en_char():
            ch_spacing = int(self.char_spacing_en * length)
        else:
            ch_spacing = int(self.char_spacing_cn * length)
        return int(ch_spacing)

    def create_layout_of_text(self, text):
        text = to_unicode(text)
        for ch in text:
            self.append_char(ch)

    def render(self):
        # self.convert_area_to_absolute()
        block = self.parent_entry.block
        ch_atom_list = self.get_sub_entry_list_with_labels(LayoutLabel.CHAR_ATOM, find_recursive=True)
        for entry in ch_atom_list:
            ch_atom = entry
            # spacing_entry = entry.get_sub_entry_list_with_labels(LayoutLabel.SPACING)[0]
            font_ch = ch_atom.font_ch
            valid_rect = font_ch.get_valid_rect(direction=self.direction)
            block_ch = font_ch.block
            block_ch = block_ch.cut_with_rect(valid_rect)
            dst_rect = ch_atom.owned_area_abs.rect.copy()
            block.paste(block_ch, top=dst_rect.top, left=dst_rect.left)


class LayoutTextLine(LayoutTextLineBase):
    def __init__(self, direction, char_spacing_cn=None, char_spacing_en=None,
                 owned_area=Area()):
        super(LayoutTextLine, self).__init__(char_spacing_cn=char_spacing_cn, char_spacing_en=char_spacing_en,owned_area=owned_area, direction=direction)


class LayoutTextBase(LayoutLinearBase):
    def __init__(self, line_spacing=None, char_spacing_cn=None, char_spacing_en=None, owned_area=Area(), direction=Direction(Direction.TO_BOTTOM)):
        super(LayoutTextBase, self).__init__(owned_area=owned_area, direction=direction)
        self.line_spacing = line_spacing or default_setting.line_spacing
        self.char_spacing_cn = char_spacing_cn
        self.char_spacing_en = char_spacing_en

    def get_line_spacing(self, line_height):
        return int(self.line_spacing * line_height)

    def get_cur_line(self, new_line_height):
        lines_entry = self.get_sub_entry_list_with_labels(LayoutLabel.TEXT_LINE)
        line_index = len(lines_entry) - 1
        if line_index < 0:
            signal = self.append_line(ask_value=new_line_height)
            if signal == LayoutSignal.OUT_OF_SPACE:
                return signal    # out of space.
            lines_entry = self.get_sub_entry_list_with_labels(LayoutLabel.TEXT_LINE)
        return lines_entry[-1]

    def append_line(self, ask_value=None):
        layout_line = LayoutTextLine(direction=Direction(Direction.TO_BOTTOM), char_spacing_cn=self.char_spacing_cn, char_spacing_en=self.char_spacing_en)
        signal = self.append_entry(layout_line, ask_value=ask_value)
        if signal == LayoutSignal.OUT_OF_SPACE:
            return signal    # out of space.
        layout_line_spacing = LayoutTextLineSpacing(direction=self.direction)
        line_spacing = self.get_line_spacing(line_height=ask_value)
        signal = self.append_entry(layout_line_spacing, ask_value=line_spacing)
        if signal == LayoutSignal.OUT_OF_SPACE:
            pass    # out of space, ignore.
        return LayoutSignal.NORMAL

    def append_text(self, text):
        line_height = 246
        cur_line = self.get_cur_line(new_line_height=line_height)
        text = to_unicode(text)
        for ch in text:
            print '<LayoutTextVertical.append_text> ch: %s' % ch
            signal = cur_line.append_char(ch)
            # 一直分配行,直到可以放下 char. 当没有足够的行时, 返回 LayoutSignal.OUT_OF_SPACE
            while signal == LayoutSignal.OUT_OF_SPACE:
                print 'LayoutSignal.OUT_OF_SPACE'
                line_signal = self.append_line(ask_value=line_height)
                if line_signal == LayoutSignal.OUT_OF_SPACE:
                    return line_signal
                cur_line = self.get_cur_line(new_line_height=line_height)
                signal = cur_line.append_char(ch)

    def render(self):
        self.convert_area_to_absolute()
        block = Block(width=self.owned_area.rect.right, height=self.owned_area.rect.bottom)
        self.block = block
        for entry in self.sub_entry_iter():
            if entry.label is not LayoutLabel.TEXT_LINE:
                continue
            entry.render()
        # block.draw_rect(self.owned_area.rect, width=5)

        for entry in self.get_sub_entry_list_with_labels(LayoutLabel().frame_label_list, find_recursive=True):
            block.draw_rect(entry.owned_area_abs.rect, width=5, color=Palette.blue, draw_inside=True)

        for entry in self.get_sub_entry_list_with_labels(LayoutLabel().spacing_label_list, find_recursive=True):
            block.draw_rect(entry.owned_area_abs.rect, width=3, color=Palette.black, draw_inside=True)

        for entry in self.get_sub_entry_list_with_labels(LayoutLabel().atom_label_list, find_recursive=True):
            block.draw_rect(entry.owned_area_abs.rect, width=2, color=Palette.red, draw_inside=True)
        block.to_file('text.jpg')


class LayoutText(LayoutTextBase):
    def __init__(self, direction, char_spacing_cn=None, char_spacing_en=None, owned_area=Area()):
        super(LayoutText, self).__init__(char_spacing_cn=char_spacing_cn, char_spacing_en=char_spacing_en,
                                         owned_area=owned_area, direction=direction)

#
# class LayoutTextHorizontal(LayoutTextBase):
#     def __init__(self, char_spacing_cn=None, char_spacing_en=None,
#                  owned_area=Area(), direction=Direction(Direction.TO_LEFT)):
#         super(LayoutTextHorizontal, self).__init__(char_spacing_cn=char_spacing_cn, char_spacing_en=char_spacing_en,
#                                                    owned_area=owned_area, direction=direction)


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
    owned_area = Area(rect=PosRect(top=0, bottom=2500, left=0, right=3000))
    text_line = LayoutTextLine(direction=Direction(Direction.TO_LEFT), owned_area=owned_area)
    text_line.create_layout_of_text('hi,我们都是好孩子')
    text_line.render()


def test_of_layout_text():
    owned_area = Area(rect=PosRect(top=0, bottom=2500, left=0, right=3000))
    text = """在开罗以南700千米处的尼罗河东岸。 遗址占据当时底比斯东城的北半部。通过斯芬克斯（见狮身人面像）大道与南面1千米的卢克索相接，那里另有一座阿蒙神庙。由于中王国和新王国各朝都是从底比斯起家而统治全国的，底比斯的地方神阿蒙神被当做王权的保护神，成为埃及众神中最重要的一位。这里的阿蒙神庙也成"""

    # text = """在开罗以南700千米处的尼罗河东岸"""
    layout_text = LayoutText(owned_area=owned_area, direction=Direction(Direction.TO_LEFT))
    print 'layout_text.direction.direction', layout_text.direction.direction
    layout_text.append_text(text)
    layout_text.render()

if __name__ == '__main__':
    test_of_layout_text()

