# -*- coding: UTF-8 -*-

"""
Desc: block is the base obj of render.
Note: the base unit 'pix'.

---------------------------------------
# 2016/04/02   kangtian         created

"""

import os
import random
import struct
import numpy as np
from PIL import Image, ImageDraw
from image.base import ColorMode, RGB
from image.base import Palette
from image.base import PosRect, PosPoint2D


class BlockBase(object):
    def __init__(self, inst, width, height, color_mode=ColorMode.RGB):
        self.color_mode = color_mode
        self.width = width
        self.height = height
        self.inst = inst
        self.file_path = None
        self.bg_color = Palette.white
        self.fg_color = Palette.black

    def from_file(self, file_path):
        pass

    def to_file(self, file_path):
        pass

    @staticmethod
    def get_new_width_height(width, height, new_width=None, new_height=None):
        if width is None or height is None:
            raise ValueError('Width and Height can not be None.')
        if new_height and not new_width:
            new_width = width * (float(new_height) / height)
        elif new_width and not new_height:
            new_height = height * (float(new_width) / width)
        if not new_width and not new_height:
            new_width, new_height = width, height
        return int(new_width), int(new_height)


class BlockWithOpenCV(BlockBase):
    def __init__(self, inst=None, width=None, height=None, color=None, color_mode=ColorMode.RGB):
        super(BlockWithOpenCV, self).__init__(inst, width=width, height=height, color_mode=color_mode)


class BlockWithPillow(BlockBase):
    color_mode_mapping = {
        ColorMode.RGB: 'RGB',
        ColorMode.BGR: 'BGR',
        ColorMode.RGBX: 'RGBX',
        ColorMode.PALETTE: 'P',
        ColorMode.GREYSCALE: 'L',
        ColorMode.BIT1: '1'
    }

    def __init__(self, inst=None, width=None, height=None, color=None, color_mode=ColorMode.RGB):
        super(BlockWithPillow, self).__init__(inst, width=width, height=height, color_mode=color_mode)
        if not self.inst and width and height and color_mode:
            size = self.get_size_with(width, height)
            color = color or self.get_color_with_rgb(self.bg_color)
            mode = self.get_color_mode(color_mode)
            self.inst = Image.new(mode=mode, size=size, color=color)
            print 'New Block: (%s, %s)' % (width, height)
        if self.inst:
            self.set_attr_use_inst()

    def from_file(self, file_path):
        try:
            im = Image.open(file_path)
            print type(im)
        except IOError:
            raise IOError('Open file error: %s' % file_path)
        print(im.format, im.size, im.mode)
        self.inst = im
        self.set_attr_use_inst()
        return self

    def to_file(self, file_path):
        if self.inst is not None:
            self.inst.save(file_path)
        else:
            raise Exception("Fail save to file, the inst is None.")
        self.file_path = file_path

    def open_file(self, file_path=None):
        file_path = file_path or self.file_path
        cmd = 'open %s' % file_path
        os.system(cmd)

    @property
    def band_num(self):
        mode = self.inst.mode
        if mode in ('RGB', 'BGR', 'RGB;L'):
            return 3
        elif mode in ('L', 'L;1', 'P'):
            return 1
        else:
            return 1

    @staticmethod
    def get_size_with(width, height):
        size = (width, height)
        return size

    @staticmethod
    def get_color_with_rgb(rgb_tuple):
        color = tuple(rgb_tuple)
        return color

    def get_color_mode(self, color_mode):
        """
        :Note: see mode of PIL: http://effbot.org/imagingbook/decoder.htm
        :param color_mode:
        :return:
        """
        mode = self.color_mode_mapping[color_mode]
        return mode

    @staticmethod
    def get_box_with(top, right, bottom, left):
        box = (left, top, right, bottom)
        return box    # The box is a 4-tuple defining the left, upper, right, and lower pixel

    def set_inst(self, inst):
        self.inst = inst
        self.set_attr_use_inst()

    def set_attr_use_inst(self):
        self.height = self.inst.size[1]
        self.width = self.inst.size[0]
        self.color_mode = str(self.inst.mode)    # notice

    def resize(self, width=None, height=None):
        width, height = self.get_new_width_height(self.width, self.height, width, height)
        new_inst = self.inst.resize((width, height))    # para: resample=NEAREST
        return BlockWithPillow(new_inst)

    def copy(self):
        new_inst = self.inst.copy()
        return BlockWithPillow(new_inst)

    def rotate(self, degrees, expand=True):
        new_inst = self.inst.rotate(degrees, expand=expand)
        return BlockWithPillow(new_inst)

    def cut(self, top, right, bottom, left):
        box = self.get_box_with(top, right, bottom, left)
        new_inst = self.inst.crop(box=box)
        return BlockWithPillow(new_inst)

    def cut_with_rect(self, pos_rect):
        pos_rect.top = 0 if pos_rect.top is None else pos_rect.top
        pos_rect.left = 0 if pos_rect.left is None else pos_rect.left
        pos_rect.bottom = self.inst.height if pos_rect.bottom is None else pos_rect.bottom
        pos_rect.right = self.inst.width if pos_rect.right is None else pos_rect.right
        return self.cut(top=pos_rect.top, right=pos_rect.right, bottom=pos_rect.bottom, left=pos_rect.left)

    def paste(self, block, left, top, right=None, bottom=None):
        """
        :Note: not return a new image.
        :param block: will be paste to block.
        :param left: 
        :param top:
        :param right:
        :param bottom:
        :return:
        """
        height = bottom - top if bottom is not None else None
        width = right - left if right is not None else None
        width, height = self.get_new_width_height(block.width, block.height, width, height)
        if right is not None or bottom is not None:
            block = block.resize(width=width, height=height)
        right, bottom = left + width, top + height
        top, bottom = int(top), int(bottom)
        left, right = int(left), int(right)
        # print 'paste', (top, right, bottom, left)
        box = self.get_box_with(top, right, bottom, left)
        self.inst.paste(block.inst, box)
        return self

    def paste_with_rect(self, block, pos_rect):
        return self.paste(block, top=pos_rect.top, right=pos_rect.right, bottom=pos_rect.bottom, left=pos_rect.left)

    def set_pix(self, color, point=None, x=None, y=None):
        if point is not None:
            xy = (point.x, point.y)
        else:
            xy = (x, y)
        self.inst.putpixel(xy, color)

    def get_pix(self, point=None, x=None, y=None):
        if point is not None:
            xy = (point.x, point.y)
        else:
            xy = (x, y)
        return self.inst.getpixel(xy)

    def draw_line(self, pos_point_0, pos_point_1, color=None, width=1):
        color = color or self.fg_color
        color = self.color_for_mode(color)
        draw = ImageDraw.Draw(self.inst)
        draw.line((pos_point_0.x, pos_point_0.y, pos_point_1.x, pos_point_1.y), fill=color, width=width)
        del draw

    def draw_rect(self, pos_rect, color=None, width=1, draw_inside=True):
        color = color or self.fg_color
        r = pos_rect.copy()
        if draw_inside:
            d_value = -int(width / 2)
            r.delta_size(d_width=d_value, d_height=d_value)
        draw = ImageDraw.Draw(self.inst)
        p0, p1 = PosPoint2D(x=r.left, y=r.top), PosPoint2D(x=r.right, y=r.top)
        p2, p3 = PosPoint2D(x=r.right, y=r.bottom), PosPoint2D(x=r.left, y=r.bottom)
        self.draw_line(p0, p1, color=color, width=width)
        self.draw_line(p1, p2, color=color, width=width)
        self.draw_line(p2, p3, color=color, width=width)
        self.draw_line(p3, p0, color=color, width=width)
        del draw

    def draw_rect_with_filled(self, pos_rect, fill=None, outline=None):
        fill = fill or self.fg_color
        outline = outline or self.fg_color
        r = pos_rect
        draw = ImageDraw.Draw(self.inst)
        draw.rectangle([(r.top, r.left), (r.right, r.bottom)], fill=fill, outline=outline)
        del draw

    def is_fill_with_color_slow(self, color):
        color = self.color_for_mode(color)
        is_fill_with_color = True
        for x in range(self.width):
            for y in range(self.height):
                c = self.get_pix(x=x, y=y)
                if c != color:
                    is_fill_with_color = False
                    break
            if not is_fill_with_color:
                break
        return is_fill_with_color

    def is_fill_with_color(self, color, is_exact=True, sample_percent=0.01):
        if not is_exact and not (sample_percent and 0 < sample_percent < 1.0):
            raise ValueError('is_exact Must be True if not sampling')
        color = self.color_for_mode(color)
        if isinstance(color, int):
            color = (color, )
        is_fill_with_color = True
        band_num = self.band_num
        for i in range(band_num):
            band_data = self.inst.getdata(band=i)
            len_band = len(band_data)
            color_value = color[i]
            if sample_percent and 0 < sample_percent < 1.0:
                step = int(len_band * sample_percent)
                sample = range(0, len_band, step)
                for index in sample:
                    if band_data[index] != color_value:
                        is_fill_with_color = False
                        break
                if not is_fill_with_color:
                    break
            if is_exact:
                if sum(band_data) != color_value * len_band:
                    is_fill_with_color = False
                    break
        return is_fill_with_color

    def get_mbr_rect_use_numpy(self, color):
        color = self.color_for_mode(color)
        if isinstance(color, int):
            color = (color, )
        band_num = self.band_num
        mbr_list = []
        width, height = self.width, self.height
        for i in range(band_num):
            band_array = np.array(self.inst.getdata(band=i))
            image = band_array.reshape((height, width))
            color_value = color[i]
            mbr = PosRect(top=0, left=0, bottom=height, right=width)
            row_in = False
            for y in range(height):
                row = image[y]
                # print 'Row: %3d' % y, ''.join(['%d ' % (0 if d < 128 else 1) for d in row])
                if sum(row) != color_value * width and not row_in:
                    mbr.top = y
                    row_in = True
                if sum(row) == color_value * width and row_in:
                    mbr.bottom = y
                    row_in = False
                    break
            column_in = False
            image_t = image.T
            for x in range(width):
                column = image_t[x]
                # print 'Column: %3d' % x, ''.join(['%d ' % (0 if d < 128 else 1) for d in column])
                if sum(column) != color_value * height and not column_in:
                    mbr.left = x
                    column_in = True
                if sum(column) == color_value * height and column_in:
                    mbr.right = x
                    column_in = False
                    break
            print 'mbr: ', mbr
            mbr_list.append(mbr)
            break
        mbr_top = max([mbr.top for mbr in mbr_list])
        mbr_left = max([mbr.left for mbr in mbr_list])
        mbr_bottom = min([mbr.bottom for mbr in mbr_list])
        mbr_right = min([mbr.right for mbr in mbr_list])
        mbr_rect = PosRect(top=mbr_top, left=mbr_left, bottom=mbr_bottom, right=mbr_right)
        return mbr_rect

    def get_mbr_rect(self, color, sample_percent=None):
        color = self.color_for_mode(color)
        if isinstance(color, int):
            color = (color, )
        band_num = self.band_num
        mbr_list = []
        width, height = self.width, self.height

        for i in range(band_num):
            band = list(self.inst.getdata(band=i))
            color_value = color[i]
            mbr = PosRect(top=0, left=0, bottom=height, right=width)
            step_height = int(height * sample_percent) if 0 < sample_percent < 0.1 else 1
            for y in range(0, height, step_height):
                row = band[y*width: y*width+width]
                # print 'Row: %3d' % y, ''.join(['%d ' % (0 if d < 128 else 1) for d in row])
                if sum(row) != color_value * width:
                    mbr.top = max(y - step_height, 0)
                    break
            for y in range(height - 1, -1, -step_height):
                row = band[y*width: y*width+width]
                if sum(row) != color_value * width:
                    mbr.bottom = min(y + step_height, height - 1)
                    break
            step_width = int(width * sample_percent) if 0 < sample_percent < 0.1 else 1
            for x in range(0, width, step_width):
                column = [band[y*width+x] for y in range(height)]
                if sum(column) != color_value * height:
                    mbr.left = max(x - step_width, 0)
                    break
            for x in range(width - 1, -1, -step_width):
                column = [band[y*width+x] for y in range(height)]
                if sum(column) != color_value * height:
                    mbr.right = min(x + step_width, width - 1)
                    break
            mbr_list.append(mbr)
        mbr_top = max([mbr.top for mbr in mbr_list])
        mbr_left = max([mbr.left for mbr in mbr_list])
        mbr_bottom = min([mbr.bottom for mbr in mbr_list])
        mbr_right = min([mbr.right for mbr in mbr_list])
        mbr_rect = PosRect(top=mbr_top, left=mbr_left, bottom=mbr_bottom, right=mbr_right)
        return mbr_rect

    def color_for_mode(self, rgb_color, mode=None):
        mode = mode or self.inst.mode
        color = None
        if mode == '1':
            avg = (rgb_color.R + rgb_color.G + rgb_color.B) / 3.0
            color = 0 if avg < 128 else 255
        elif mode == 'RGB':
            color = rgb_color
        return color

    def to_binary(self):
        bytes_data = self.inst.tobytes()
        mode_str = self.inst.mode
        bytes_info = struct.pack('32sii', mode_str, self.width, self.height)
        binary = bytes_info + bytes_data
        return binary

    def from_binary(self, binary):
        bytes_info_size = struct.calcsize('32sii')
        mode_str, width, height = struct.unpack('32sii', binary[:bytes_info_size])
        data_bytes = binary[bytes_info_size:]
        mode_str = ''.join([c for c in mode_str if c.isalnum() or c in (';', ' ')])
        inst = Image.frombytes(mode_str, (height, width), data_bytes)    # note: doc say size is tuple(width, height)...
        self.set_inst(inst)
        return self


class Block(BlockWithPillow):
    def __init__(self, inst=None, width=None, height=None, color=None, color_mode=ColorMode.RGB):
        super(Block, self).__init__(inst, width=width, height=height, color_mode=color_mode)


def get_block(type='Pillow', inst=None, width=None, height=None, color=None, color_mode=ColorMode.RGB):
    """
    :param type: 'Pillow' | 'OpenCV
    :param inst:
    :param width:
    :param height:
    :param color:
    :param color_mode:
    :return:
    """
    if type == 'Pillow':
        inst = BlockWithPillow(inst, width=width, height=height, color_mode=color_mode)
    elif type == 'OpenCV':
        inst = BlockWithOpenCV(inst, width=width, height=height, color_mode=color_mode)
    else:
        inst = BlockWithPillow(inst, width=width, height=height, color_mode=color_mode)
    return inst


def test_of_mbr_rect():
    block = Block().from_file('/Users/kangtian/Documents/Master/tinydoc/res/font/char_zi.jpg')
    rect = block.get_mbr_rect(Palette.white)
    print rect


if __name__ == '__main__':
    block = Block(width=1600, height=900)
    os.system('ls')
    block.draw_line(PosPoint2D(0, 0), PosPoint2D(300, 300), width=5)
    rect = PosRect(top=300, left=300, right=500, bottom=500)
    # block.draw_rect_with_filled(rect)
    block.draw_rect(rect, width=5)
    block.to_file('block.jpg')


