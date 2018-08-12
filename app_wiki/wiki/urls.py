#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import TagView, add_tag, del_tag, update_tag, wiki_backend, wiki_content_backend
from .views import WiKiContentEdit, add_title, del_title, upload_image, del_comment, move_title, upload_paste_image

from .views import wiki_list, wiki_detail, AddWiKiComment, change_theme, theme_setting, delete_theme, history_search, history_search_delete

# 自定义权限
from DjangoMyStarMeow.permission import permission_forbidden  # 403表示只能超级管理员，401表示必须登录


urlpatterns = [
    url(r'^$', wiki_backend, name='wiki_index'),
    url(r'^tags/$', permission_forbidden(http_exception=403)(TagView.as_view()), name='tags'),
    url(r'^add_tag/$', add_tag, name='add_tag'),
    url(r'^del_tag/(?P<tag_id>\d+)/$', del_tag, name='del_tag'),
    url(r'^update_tag/$', update_tag, name='update_tag'),
    url(r'^wiki_backend/$', wiki_backend, name='wiki_backend'),
    url(r'wiki_backend/title_id_(?P<title_id>\d+)/$', permission_forbidden(http_exception=403)(wiki_content_backend), name='wiki_content_backend'),
    url(r'^edit/title_id_(?P<title_id>\d+)/$', permission_forbidden(http_exception=403)(WiKiContentEdit.as_view()), name='wiki_edit'),
    url(r'^add_title/$', permission_forbidden(http_exception=403)(add_title), name='add_title'),
    url(r'^del_title/$', permission_forbidden(http_exception=403)(del_title), name='del_title'),

    url(r'^upload_image/$', upload_image, name='upload_image'),
    url(r'^upload_paste_image/$', upload_paste_image, name='upload_paste_image'),
    url(r'^del_comment/$', permission_forbidden(http_exception=403)(del_comment), name='del_comment'),  # 删除评论

    url(r'^move_title/$', move_title, name='move_title'),

    # 前端
    url(r'^wiki_list/title_id_(?P<title_id>\d+)/detail/$', wiki_detail, name='wiki_detail'),
    url(r'^wiki_list/(?P<title_id>\d+)/$', wiki_list, name='wiki_list'),
    url(r'^wiki_list/$', wiki_list, name='wiki_list_index'),
    url(r'^add_comment/$', AddWiKiComment.as_view(), name='add_comment'),
    url(r'^change_theme/$', change_theme, name='change_theme'),
    url(r'^theme_setting/$', theme_setting, name='theme_setting'),
    url(r'^delete_theme/$', delete_theme, name='delete_theme'),
    url(r'^history_search/$', history_search, name='history_search'),
    url(r'^history_search_delete/$', history_search_delete, name='history_search_delete'),
]

