from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^accounts/', include("django.contrib.auth.urls")),
                       url(r'^accounts/', include('allauth.urls')),
                       url(r'^', include('tavern.urls')),
                       url(r'^user/', include('accounts.urls')),
                       )
