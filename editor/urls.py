# -*- coding: utf-8 -*-

import views

from django.conf.urls import patterns, url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'edit/$', views.reply_to_edit_page),
    url(r'edit/sync_content/$', views.reply_to_sync_content),
)
