from django.conf.urls import patterns, url

from tavern import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^groups/(?P<slug>[\w-]+)',
                           views.group_details, name='group_details'),
                       url(r'^events/(?P<slug>[\w-]+)',
                           views.event_details, name='event_details'),
                       url(r'^create_group/',
                           views.create_group, name='create_group'),
                       url(r'^(?P<slug>[\w-]+)/tavern_group_update',
                           views.tavern_group_update,
                           name='tavern_group_update'),
                       url(r'^create_event/',
                           views.create_event, name='create_event'),
                       url(r'^(?P<slug>[\w-]+)/tavern_event_update',
                           views.tavern_event_update,
                           name='tavern_event_update'),
                       url(r'^change_password',
                           views.change_password, name='change_password'),
                       url(r'^signup', views.signup, name='signup'),
                       )
