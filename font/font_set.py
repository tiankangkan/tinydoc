# -*- coding: UTF-8 -*-

"""
Desc: manage fonts.
Note:

---------------------------------------
# 2016/04/02   kangtian         created

"""

import gzip
import cStringIO as StringIO
import os
import time
import cPickle as Pickle

from image.base import PosRect, Palette
from image.block import Block
from font.font_char import FontChar
from tinydoc_setting import FONT_DIR
from k_util.str_op import to_unicode


FONT_VERSION = '1.0'


class FontType(object):
    HFONT = '.hfont'
    TTF = '.ttf'
    BITMAP_FONT = '.bmp'
    GZIP_FONT = '.gzipf'


class Font(object):
    def __init__(self, font_path, font_type, font_name=None, do_load=True):
        self.ch_set = dict()
        self.font_name = font_name is not None or 'font_unknown'
        self.font_path = font_path
        self.font_type = font_type
        self.is_load = False
        self.version = FONT_VERSION
        self.ch_width = None
        self.ch_height = None
        if do_load:
            self.load_font()
            self.is_load = True

    def load_font(self, font_path=None):
        if self.font_type == FontType.HFONT:
            self.load_hfont(font_path)
        elif self.font_type == FontType.TTF:
            self.load_ttf_font(font_path)
        elif self.font_type == FontType.BITMAP_FONT:
            self.load_bitmap_font(font_path)
        elif self.font_type == FontType.GZIP_FONT:
            self.load_gzip_font()
        else:
            raise ValueError('Wrong font type: %s' % self.font_type)
        self.do_after_load_font()

    def do_after_load_font(self):
        self.try_make_up_special_chars()
        sample_ch = self.get_char('a')
        sample_block = sample_ch.block
        self.ch_width, self.ch_height = sample_block.width, sample_block.height

    def try_make_up_special_chars(self):
        if not self.has_char(' '):
            font_ch = self.create_empty_font_char_with_width(width=0.5)
            self.put_char(' ', font_ch)

    def load_hfont(self, font_path=None):
        ch_set = self.ch_set
        ch_set[u'字'] = Block().from_file('/Users/kangtian/Documents/Master/tinydoc/res/test/image/char_zi.jpg')

    def load_bitmap_font(self, font_path=None):
        from font_bitmap import FontBitmap
        font_path = font_path or self.font_path
        font_name, font_type = os.path.splitext(os.path.basename(font_path))
        ch_set = FontBitmap(font_path=font_path).get_char_set()
        self.ch_set = ch_set
        self.font_name = font_name
        self.font_type = FontType.BITMAP_FONT
        self.font_path = font_path
        self.is_load = True

    def load_ttf_font(self, font_path=None):
        pass

    def has_char(self, ch):
        return ch in self.ch_set

    def get_char(self, ch, replace_ch=' '):
        ch = to_unicode(ch)
        if not self.is_load:
            print 'Load font %s, wait ...' % self.font_name
            self.load_font()
        if not self.has_char(ch):
            print 'Waring: not found char: %s, replace with %s' % (ch, replace_ch)
            return self.get_char(replace_ch)
        return self.ch_set[ch]

    def put_char(self, ch, font_ch):
        self.ch_set[ch] = font_ch

    def to_gzip_font(self, file_path=None, file_obj=None):
        t_start = time.time()
        font_entry = dict()
        font_entry['ch_set'] = dict()
        font_entry['font_name'] = self.font_name
        font_entry['font_type'] = self.font_type
        count = 0
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, self.font_name+FontType.GZIP_FONT)
        for ch in self.ch_set:
            ch_obj = self.ch_set[ch]
            ch_block = ch_obj.block
            if ch_block:
                file_obj_tmp = StringIO.StringIO()
                g = gzip.GzipFile(mode="wb", compresslevel=9, fileobj=file_obj_tmp)
                ch_data = bytearray(ch_block.to_binary())
                ch_buffer = buffer(ch_data)
                g.write(ch_buffer)
                g.close()
                file_obj_tmp.flush()
                gzip_data = file_obj_tmp.getvalue()
                ch_obj.block = gzip_data
                font_entry['ch_set'][ch] = ch_obj
                # print len(gzip_data), len(ch_data)
            count += 1
            if count % 500 == 0:
                print 'store_with_gzip: %s/%s | %.1f%%' % (count, len(self.ch_set), (count*100.0/len(self.ch_set)))
        print "<Font.to_gzip_font> Cost Time %s sec." % (time.time() - t_start)
        if file_obj is None:
            Pickle.dump(font_entry, open(file_path, 'wb'))
            print "<Font.to_gzip_font> Saved to file: %s" % file_path
        else:
            Pickle.dump(font_entry, file_obj)

    def load_gzip_font(self, file_path=None, file_obj=None):
        t_start = time.time()
        file_path = file_path or self.font_path
        if file_obj:
            font_entry = Pickle.load(file_obj)
        else:
            with open(file_path, 'rb') as fp:
                font_entry = Pickle.load(fp)
        if font_entry is None:
            raise IOError('Can not parse font file: %s' % file_path)
        unzip_ch_set = font_entry['ch_set']
        ch_set = dict()
        for ch in unzip_ch_set:
            ch_obj = unzip_ch_set[ch]
            gzip_data = ch_obj.block
            file_obj_tmp = StringIO.StringIO()
            file_obj_tmp.write(gzip_data)
            file_obj_tmp.flush()
            file_obj_tmp.reset()
            g = gzip.GzipFile(mode="rb", fileobj=file_obj_tmp)
            ch_data = g.read()
            while True:
                chunk = g.read()
                if not chunk:
                    break
                ch_data += chunk
            ch_block = Block().from_binary(ch_data)
            ch_obj.block = ch_block
            ch_set[ch] = ch_obj
            g.close()
        self.ch_set = ch_set
        self.font_path = file_path
        self.font_name = font_entry['font_name']
        self.font_type = font_entry['font_type']
        self.version = font_entry.get('version', FONT_VERSION)
        self.is_load = True
        print "<Font.load_gzip_font> Cost Time %s sec." % (time.time() - t_start)
        return self

    def create_empty_font_char_with_width(self, width, height=1):
        sample_ch = self.get_char('a')
        sample_block = sample_ch.block
        ch_width, ch_height = sample_block.width, sample_block.height
        mbr_width = int(width * ch_width)
        mbr_height = int(height * ch_height)
        block = Block(width=ch_width, height=ch_height)
        mbr_rect = PosRect(top=0, left=0, right=mbr_width, bottom=mbr_height)
        font_ch = FontChar(ch=' ', block=block, mbr_rect=mbr_rect)
        return font_ch


class FontSet(object):
    pre_load_font_info = [
        dict(font_path=os.path.join(FONT_DIR, 'hunlu.gzipf'), font_type=FontType.GZIP_FONT)
    ]

    def __init__(self, default_font_name=None):
        self.font_set = {}
        for font_info in self.pre_load_font_info:
            self.load_font(font_path=font_info['font_path'], font_type=font_info['font_type'])
        self.default_font_name = default_font_name or None

    def load_font(self, font_path, font_type):
        font_path = to_unicode(font_path)
        font = Font(font_path=font_path, font_type=font_type, do_load=True)
        font_name = font.font_name
        self.font_set[font_name] = font

    def get_font(self, font_name=None):
        font_name = font_name or self.default_font_name
        font_name = to_unicode(font_name)
        if font_name not in self.font_set:
            raise ValueError('Font name not in font_set: %s' % font_name)
        return self.font_set[font_name]

    def get_char(self, ch, font_name=None):
        # ch = to_unicode(ch)
        font_name = font_name or self.default_font_name
        i_font = self.get_font(font_name)
        font_ch = i_font.get_char(ch)
        return font_ch

    def get_font_names(self):
        return self.font_set.keys()

global_font_set = FontSet(default_font_name='hunlu')


def convert_bmp_font_to_zip_font(font_path):
    i_font = Font(font_path=font_path, font_type=FontType.BITMAP_FONT)
    i_font.to_gzip_font(file_path=FONT_DIR)

if __name__ == '__main__':
    # font_set = FontSet()

    convert_bmp_font_to_zip_font(os.path.join(FONT_DIR, 'hunlu.bmp'))
    # global_font_set.get_char(',')
    # print global_font_set.get_font().ch_set.keys()

    # print '%s' % to_unicode(',')

    # font = Font(font_path=os.path.join(FONT_DIR, 'hunlu.gzipf'), font_type=FontType.GZIP_FONT)
    # print font.ch_set.keys()
    # print u'啊' in font.ch_set.keys()
    # ch_block = font.get_char(u'啊')
    # print type(ch_block)
    # ch_block.to_file('啊.jpg')
    # print font.font_name
