# -*- coding: utf-8 -*-

import json
import base64
import traceback
import os
import shutil

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
    try:
        req = django_util.get_request_body(request)
        doc_identify = req.get('doc_identify', 'MyDocument')
        editor_content = req.get('editor_content', '')
        need_pdf = req.get('need_pdf', 'false')
        need_pdf = True if need_pdf == 'true' else False
        file_name = req.get('file_name', doc_identify)
        text_content = get_text_of_html(editor_content)
        print editor_content, text_content
        doc = DocSession(doc_identify=doc_identify)
        doc.append_text(text_content)
        doc.render(to_pdf=True, to_image=True)
        # image_path = doc.doc_info['image_list'][-1]
        image_list = list()
        # print 'image_path: %s' % image_path
        for image_path in doc.doc_info['image_list']:
            try:
                with open(image_path, "rb") as f:
                    content = f.read()
                    content_base64 = base64.b64encode(content)
                    image_list.append(content_base64)
            except IOError:
                print traceback.format_exc()
                continue
                # red = Image.new('RGBA', (1, 1), (255, 0, 0, 0))
                # response = HttpResponse(content_type="image/jpeg")
                # red.save(response, "JPEG")
                # return response
        print 'need_pdf', need_pdf
        if need_pdf:
            pdf_path = doc.get_pdf_path()
            pdf_with_filename = os.path.join(os.path.dirname(pdf_path), '%s.pdf' % file_name)
            shutil.copy(pdf_path, pdf_with_filename)
            url_download = '/data/%s/%s' % (doc_identify, os.path.basename(pdf_path))
            resp = dict(status='ok', data=url_download)
        else:
            resp = dict(status='ok', data=image_list)
        return HttpResponse(json.dumps(resp))
    except:
        print traceback.format_exc()
