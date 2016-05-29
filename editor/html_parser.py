# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup


support_tag_list = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'span']


def parse_html(html_str):
    # html_str = """<h1>我的世界 ！</h1>
    #
    #     <p>我有许多<u>这样的好东西</u></p>
    #
    #     <p>&nbsp;</p>
    #
    #     <p>I&#39;m an instance of <a href="http://ckeditor.com">CKEditor</a>.&nbsp;</p>"""
    soup = BeautifulSoup(html_str, 'html.parser')
    res = soup.find_all(support_tag_list)
    return res


def get_text_of_html(html_str):
    html_set = parse_html(html_str)
    res = '\n'.join([item.get_text() for item in html_set])
    res.replace(u'\xa0', u' ')
    return res


if __name__ == '__main__':
    get_text_of_html('')
