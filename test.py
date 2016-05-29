# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup


def parse_html(html_str):
    html_str = """<h1>我的世界 ！</h1>

<p>我有许多这样的好东西</p>

<p>&nbsp;</p>

<p>I&#39;m an instance of <a href="http://ckeditor.com">CKEditor</a>.&nbsp;</p>"""
    soup = BeautifulSoup(html_str, 'html.parser')
    for item in soup.find_all(['p', 'h1']):
        print item.name
        print item.get_text()


parse_html(1)
