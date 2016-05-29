# -*- coding: utf-8 -*-

import json
import base64
from html_parser import get_text_of_html
from PIL import Image

from django.shortcuts import render_to_response, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from k_util import django_util
from render.render_api import render_text_to_img
from doc_session.session import DocSession

@csrf_exempt
def reply_to_edit_page(request):
    return render_to_response('edit_page.html')


@csrf_exempt
def reply_to_sync_content(request):
    req = django_util.get_request_body(request)
    doc_identify = req.get('doc_identify', 'MyDocument')
    editor_content = req.get('editor_content', '')
    text_content = get_text_of_html(editor_content)
    print editor_content, text_content
    doc = DocSession(doc_identify=doc_identify)
    doc.append_text(text_content)
    doc.render(to_pdf=False)
    image_path = doc.doc_info['image_list'][-1]
    try:
        with open(image_path, "rb") as f:
            content = f.read()
            content_base64 = base64.b64encode(content)
            return HttpResponse(content_base64, content_type="text")
    except IOError:
        red = Image.new('RGBA', (1, 1), (255, 0, 0, 0))
        response = HttpResponse(content_type="image/jpeg")
        red.save(response, "JPEG")
        return response
