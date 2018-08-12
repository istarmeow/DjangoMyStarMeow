#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Version :   Ver1.0
@Author  :   LR
@License :   (C) Copyright 2013-2017, MyStudy
@Contact :   xyliurui@look
@Software:   PyCharm
@File    :   tasks.py
@Time    :   2018/7/3 14:20
@Desc    :
"""

from __future__ import unicode_literals
from django.db.models import F

from .models import WiKiContent, AuthorLog, CommentsLog
from celery import task
from DjangoMyStarMeow.mail import send_mail


@task
def increase_views(wiki_content_id):
    print("启用异步任务，访问量+1")
    return WiKiContent.objects.filter(id=wiki_content_id).update(views=F('views')+1)


@task
def send_comment_mail(subject, message):
    print("启用异步任务，发送邮件")
    send_mail("xyliurui@foxmail.com", subject, message)


@task
def create_author_log(operate, title_name, title_id, message=''):
    """
    ('update', '更新了'),
    ('delete', '删除了'),
    ('create', '创建了'),
    ('move', '移动了')
    """
    print('启用异步任务，记录作者动态日志')
    AuthorLog.objects.create(
        operate=operate,
        title_name=title_name,
        title_id=title_id,
        message=message,
    )


@task
def create_comments_log(user_name, operate, title_name, title_id, content):
    """
    ('reply', '回复了'),
    ('delete', '删除了'),
    ('create', '评论了'),
    """
    print('启用异步任务，记录评论消息日志')
    CommentsLog.objects.create(
        user_name=user_name,
        operate=operate,
        title_name=title_name,
        title_id=title_id,
        content=content,
    )


