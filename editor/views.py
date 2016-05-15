# -*- coding: utf-8 -*-

import json

from django.shortcuts import render_to_response, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from k_util import django_util

@csrf_exempt
def reply_to_edit_page(request):
    return render_to_response('edit_page.html')


def reply_to_sync_content(request):
    req =
    return HttpResponse('edit_page.html')
