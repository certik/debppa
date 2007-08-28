from django.conf.urls.defaults import *

urlpatterns = patterns('debppa.ppa.views',
    (r'^packages/$', 'ppa_packages'),
    (r'^upload/$', 'ppa_upload'),
    (r'^temp/$', 'ppa_temp'),
    (r'^contact/$', 'ppa_contact'),
    (r'^import/$', 'ppa_import'),
    (r'^build/$', 'ppa_build'),
    (r'^delete/$', 'ppa_delete'),
    (r'^buildlog/(?P<package_name>\S+)/$', 'ppa_buildlog'),
    (r'^sourcepackage/(?P<package_name>\S+)/$', 'ppa_sourcepackage'),
    (r'^sourceslist/$', 'ppa_sourceslist'),
)
