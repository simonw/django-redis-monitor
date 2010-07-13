from django.conf.urls.defaults import *
from django.http import HttpResponse
import time
from random import random

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', lambda request: time.sleep(random()) or HttpResponse('Hello!')),
    (r'^admin/(.*)', admin.site.root),
    ('^redis-monitor/$', 'django_redis_monitor.views.monitor'),
)
