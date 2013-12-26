from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings

from tavern import views

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', views.index, name='index'),
                       url(r'^accounts/', include("django.contrib.auth.urls")),
                       url(r'^groups/(?P<group_id>\d+)', views.group_details, name='group_details'),
                       url(r'^events/(?P<event_id>\d+)', views.event_details, name='event_details')
                       )

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

