#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import course, goods, other1, other2
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^other1/$', other1, name='other1'),
    url(r'^other2/$', other2, name='other2'),
    # 访问形式http://127.0.0.1:8000/test/course-0-0-0.html，
    # 第一个0代表课程分类，第二个0代表编程语言，第三个0代表课程级别
    # 0代表全部，然后递增，当选择课程分类中的第一项，第一个0就会变成1
    url(r'^course-(?P<code_id>\d+)-(?P<category_id>\d+)-(?P<level_id>\d+).html', course, name='course'),
    url(r'^goods.html$', goods, name='goods'),
    url(r'^goods-(?P<first_category_id>\d+)-(?P<sub_category_id>\d+)-(?P<tags_id>\d+)-(?P<status_id>\d+).html', goods, name='goods_filter'),
]

