#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import BlogList, BlogDetail, BlogCreate, BlogDelete, upload_paste_image, upload_image, BlogUpdate, BlogNoticeUpdate, CategoryManage, TagManage
# 自定义权限
from DjangoMyStarMeow.permission import permission_forbidden  # 403表示只能超级管理员，401表示必须登录


urlpatterns = [
    url(r'^articles/$', permission_forbidden(http_exception=403)(BlogList.as_view()), name='blog_list'),
    url(r'^category/(?P<category_id>\d+)/articles/$', permission_forbidden(http_exception=403)(BlogList.as_view()), name='blog_list_with_category'),  # 筛选分类下的列表
    url(r'^article/(?P<article_id>\d+)/detail/', permission_forbidden(http_exception=403)(BlogDetail.as_view()), name='blog_detail'),  # 博客详情
    url(r'^articles/(?P<year>\d+)/(?P<month>\d+)/$', permission_forbidden(http_exception=403)(BlogList.as_view()), name='blog_list_year_month'),  # 按月归档
    url(r'^tag/(?P<tag_id>\d+)/articles/$', permission_forbidden(http_exception=403)(BlogList.as_view()), name='blog_list_tag'),  # 按标签归档
    url(r'^search/articles/$', permission_forbidden(http_exception=403)(BlogList.as_view()), name='blog_list_search'),  # 匹配搜索
    url(r'^article/create/$', permission_forbidden(http_exception=403)(BlogCreate.as_view()), name='blog_create'),  # 创建新博客
    url(r'^article/(?P<article_id>\d+)/delete/', permission_forbidden(http_exception=403)(BlogDelete.as_view()), name='blog_delete'),  # 删除博客
    url(r'^upload_paste_image/$', permission_forbidden(http_exception=403)(upload_paste_image), name='upload_paste_image'),  # editor.md中粘贴上传图片
    url(r'^upload_image/$', permission_forbidden(http_exception=403)(upload_image), name='upload_image'),  # editor.md中工具栏上传图片
    url(r'^article/(?P<article_id>\d+)/update/', permission_forbidden(http_exception=403)(BlogUpdate.as_view()), name='blog_update'),  # 更新博客
    url(r'^draft/articles/$', permission_forbidden(http_exception=403)(BlogList.as_view()), name='blog_draft'),  # 显示草稿的列表
    url(r'^notice/(?P<slug>\w+)/edit/$', permission_forbidden(http_exception=403)(BlogNoticeUpdate.as_view()), name='blog_notice'),  # 编辑博客公告
    url(r'^manage/category/$', permission_forbidden(http_exception=403)(CategoryManage.as_view()), name='manage_category'),  # 博客分类管理
    url(r'^manage/tag/$', permission_forbidden(http_exception=403)(TagManage.as_view()), name='manage_tag'),  # 博客标签管理

    # 用户展示部分，指定template_name覆盖类视图的值，达到不同链接渲染不同的模板
    url(r'^p/articles$', BlogList.as_view(template_name='blog-list-public.html'), name='blog_list_public'),
    url(r'^p/category/(?P<category_id>\d+)/articles/$', BlogList.as_view(template_name='blog-list-public.html'), name='blog_list_with_category_public'),  # 筛选分类下的列表
    url(r'^p/article/(?P<article_id>\d+)/detail/', BlogDetail.as_view(template_name='blog-detail-public.html'), name='blog_detail_public'),  # 博客详情
    url(r'^p/articles/(?P<year>\d+)/(?P<month>\d+)/$', BlogList.as_view(template_name='blog-list-public.html'), name='blog_list_year_month_public'),  # 按月归档
    url(r'^p/tag/(?P<tag_id>\d+)/articles/$', BlogList.as_view(template_name='blog-list-public.html'), name='blog_list_tag_public'),  # 按标签归档
    url(r'^p/search/articles/$', BlogList.as_view(template_name='blog-list-public.html'), name='blog_list_search_public'),  # 匹配搜索
]