from django.conf.urls import patterns, url

from accounts import views

urlpatterns = patterns('',
                       url(r'^change_password',
                           views.change_password, name='change_password'),
                       url(r'^signup', views.signup, name='signup'),
                       url(r'^signin', views.signin, name='signin'),
                       )
