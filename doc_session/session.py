# -*- coding: UTF-8 -*-

"""
Desc: document session.
Note:

---------------------------------------
# 2016/05/29   kangtian         created

"""
import os

from k_util.file_op import make_sure_file_dir_exists
from tinydoc_setting import DATA_DIR
from layout.layout_element import LayoutDocumentBase


class DocSession(LayoutDocumentBase):
    def __init__(self, doc_identify, page_edge=None, page_size=None, color_mode=None, bg_color=None):
        self.doc_identify = doc_identify
        self.session_dir = self.get_session_dir_of_identify()
        make_sure_file_dir_exists(self.session_dir)
        super(DocSession, self).__init__(doc_identify=doc_identify, session_dir=self.session_dir, page_edge=page_edge,
                                         page_size=page_size, color_mode=color_mode, bg_color=bg_color)

    def get_session_dir_of_identify(self):
        return os.path.join(DATA_DIR, self.doc_identify)
