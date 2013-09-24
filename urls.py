from django.conf.urls.defaults import *

# Uncomment this for admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'albums.views.home'),
    (r'^album/(?P<album_id>[^/]*)/(?P<page_num>[^/]*)$', 'albums.views.album'),
    (r'^month/(?P<year>[0-9]{4})/(?P<month>[0-9]*)/(?P<page_num>[^/]*)$', 'albums.views.month'),

    (r'^admin/(.*)', admin.site.root),
)
