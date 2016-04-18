# -*- coding: UTF-8 -*-

"""
Desc: render_set contains the objects that can be rendered.
Note:

---------------------------------------
# 2016/04/02   kangtian         created

"""

from image.base import Palette, PosRect, PosPoint2D
from image.block import Block
from font.font_set import global_font_set
from layout.layout_page import DocPage


class RenderBase(object):
    def __init__(self, dst_block=None, dst_rect=None, src_block=None, src_rect=None, bg_color=None, fg_color=None):
        self.bg_color = bg_color or Palette.white
        self.fg_color = fg_color or Palette.black
        self.dst_block = dst_block
        self.dst_rect = dst_rect
        self.src_block = src_block
        self.src_rect = src_rect
        self.sub_renders = []

    def render_to_block(self):
        for render in self.sub_renders:
            render.render_to_block()
        src_block = self.src_block
        if self.src_block is None:
            return
        if self.src_rect is not None:
            src_block = src_block.cut_with_rect(self.src_rect)
        self.dst_block.paste_with_rect(src_block, self.dst_rect)

    def append_render(self, render):
        if render.dst_block is None:
            if self.src_block is not None:
                render.dst_block = self.src_block
                render.dst_rect = self.src_rect if render.dst_rect is None else render.dst_rect
            else:
                render.dst_block = self.dst_block
                render.dst_rect = self.dst_rect if render.dst_rect is None else render.dst_rect
        self.sub_renders.append(render)

    def to_image_file(self, file_path):
        if self.dst_block is None:
            self.render_to_block()
        self.dst_block.to_file(file_path)


class RenderChar(RenderBase):
    def __init__(self, ch, font_name, dst_rect=None, dst_block=None, src_rect=None, src_block=None, rotate_degree=None, rotate_center=None,
                 font_color=None, bg_color=None, fg_color=None):
        super(RenderChar, self).__init__(dst_block=dst_block, dst_rect=dst_rect, src_block=src_block, src_rect=src_rect, bg_color=bg_color, fg_color=fg_color)
        self.ch = ch
        self.font_name = font_name
        self.font_color = font_color or Palette.black
        self.rotate_degree = rotate_degree or 0
        self.rotate_center = rotate_center or PosPoint2D(0, 0)

    def render_to_block(self):
        self.src_rect = PosRect.start_from_zero()
        self.src_block = global_font_set.get_char(ch=self.ch, font_name=self.font_name)
        super(RenderChar, self).render_to_block()


class RenderText(RenderBase):
    def __init__(self, dst_rect=None, dst_block=None, src_rect=None, src_block=None, font_color=None, bg_color=None, fg_color=None):
        super(RenderText, self).__init__(dst_block=dst_block, dst_rect=dst_rect, src_block=src_block, src_rect=src_rect, bg_color=bg_color, fg_color=fg_color)
        self.font_color = font_color or Palette.black


class RenderPage(RenderBase):
    def __init__(self, doc_page, dst_rect=None, dst_block=None, src_rect=None, src_block=None, bg_color=None, fg_color=None):
        if dst_block is None:
            dst_block = Block(height=doc_page.pix_info['height_pix'], width=doc_page.pix_info['width_pix'])
        if dst_rect is None:
            dst_rect = PosRect.start_from_zero()
        print dst_block
        super(RenderPage, self).__init__(dst_block=dst_block, dst_rect=dst_rect, src_block=src_block, src_rect=src_rect, bg_color=bg_color, fg_color=fg_color)


if __name__ == '__main__':
    page = DocPage()
    print page.pix_info['height_pix']
    rect = PosRect(0, 100, 100, 0)
    page = RenderPage(page)
    text = RenderText(dst_rect=rect)
    page.append_render(text)
    ch = RenderChar(ch=u'字', font_name='kang')
    text.append_render(ch)
    page.render_to_block()
    page.to_image_file('page.jpg')



