# -*- coding: UTF-8 -*-

"""
Desc: layout base.
Note:

---------------------------------------
# 2016/05/15   kangtian         created

"""

import time
import os

from fpdf import FPDF

from layout.layout_base import Direction
from layout.layout_element import RenderPageBase, LayoutText, LayoutPageBase


def render_text_to_img(text, output_path):
    t_start = time.time()
    page = LayoutPageBase()
    page.convert_area_to_absolute()
    r = RenderPageBase(layout=page)
    r.render()
    layout_text = LayoutText(line_direction=Direction(Direction.TO_BOTTOM))
    page.append_entry(layout_text)
    layout_text.append_text(text)
    page.render()
    print 'Cost Time: %s Sec.' % (time.time() - t_start)
    r.to_image_file(output_path)
    print [text]
    os.system('open %s' % output_path)


def render_images_to_pdf(image_list):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page(format='A4')
    pdf.image('/Users/kangtian/Documents/Master/tinydoc/page.jpg', 0, 0, 210)
    pdf.output('/Users/kangtian/Documents/Master/tinydoc/page.pdf')
    for img in image_list:
        pass

if __name__ == '__main__':
    # render_text_to_img("""活动策划是提高市场占有率的有效行为，一份可执行、可操作、创意突出的活动策划案，可有效提升企业的知名度及品牌美誉度。活动策划案是相对于市场策划案而言，严格说它们同属市场策划的兄弟分支，活动策划、市场策划是相辅相成、相互联系的。市场策划和活动策划都从属于企业的整体营销思想，只有在此前提下做出的市场策划案和活动策划案才兼具整体性和延续性，也只有这样，能够有效的使受众群体同意一个品牌的文化内涵。活动策划案应遵从市场策划案的整体思路，才能够使企业保持一定的市场销售额。""", 'out.jpg')
    render_images_to_pdf([])

