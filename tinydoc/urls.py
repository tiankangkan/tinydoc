"""tinydoc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

import os
import editor.urls
from settings import STATIC_ROOT
from django.conf.urls import include, url, patterns
from django.contrib import admin

from tinydoc_setting import DATA_DIR

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^editor/', include(editor.urls)),
]


urlpatterns += patterns('django.views.static',
    url(r'^apps/(?P<path>.*)$', 'serve', {'document_root': os.path.join(STATIC_ROOT, 'apps')}),
    url(r'^jslib/(?P<path>.*)$', 'serve', {'document_root': os.path.join(STATIC_ROOT, 'jslib')}),
    url(r'^res/(?P<path>.*)$', 'serve', {'document_root': os.path.join(STATIC_ROOT, 'res')}),
    url(r'^media/(?P<path>.*)$', 'serve', {'document_root': os.path.join(STATIC_ROOT, 'media')}),
)

urlpatterns += patterns('django.views.static',
    url(r'^data/(?P<path>.*)$', 'serve', {'document_root': DATA_DIR}),
)
