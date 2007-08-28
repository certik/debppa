from django.conf.urls.defaults import *

import os.path
p = os.path.join(os.path.dirname(__file__), 'media/')

urlpatterns = patterns('',
    (r'^$', 'debppa.views.index'),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': p}),
    (r'^ppa/', include('debppa.ppa.urls')),
    (r'^admin/', include('django.contrib.admin.urls')),
)
