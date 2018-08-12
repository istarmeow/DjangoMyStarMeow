#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from event.views import event, ProcessView, start_processing, CreateEvent
from event.views import processed, confirm_processed, event_close, submit_analysis


urlpatterns = [
    url(r'^$', event, name='list'),
    url(r'^event-(?P<user_id>\d+)-(?P<status_id>\d+)-(?P<level_id>\d+)-(?P<category_id>\d+)-(?P<project_id>\d+).html$', event, name='event_filter'),
    url(r'^id/(?P<event_pk>\d+)/$', ProcessView.as_view(), name='process'),
    url(r'^start_processing/(?P<event_pk>\d+)/$', start_processing, name='start_processing'),
    url(r'^create/$', CreateEvent.as_view(), name='event_create'),
    url(r'^id/(?P<event_pk>\d+)/processed/$', processed, name='processed'),
    url(r'^id/(?P<event_pk>\d+)/processed/confirm/$', confirm_processed, name='confirm_processed'),
    url(r'^id/(?P<event_pk>\d+)/close/$', event_close, name='event_close'),
    url(r'^id/(?P<event_pk>\d+)/analysis/$', submit_analysis, name='submit_analysis'),
]

