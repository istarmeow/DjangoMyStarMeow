#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 不在使用
from django import template
from wiki.models import TitleTree


register = template.Library()


# @register.simple_tag
# def title_select():
#     all_titles = TitleTree.objects.all()
#     select = ''
#     for title in all_titles:
#         if title.is_root_node():
#             select += '<option value="{}">{} {}</option>'.format(title.id, "&nbsp;"*2, title.name.strip("*"))
#         elif title.is_leaf_node():
#             select += '<option value="{}">{} {}</option>'.format(title.id, "&nbsp;"*8, title.name)
#         elif title.is_child_node():
#             select += '<option value="{}">{} {}</option>'.format(title.id, "&nbsp;"*5, title.name)
#         else:
#             select += '<option value="{}">{}</option>'.format(title.id, title.name)
#     return select


# 实现移动文章选项
@register.simple_tag
def title_select(all_titles=TitleTree.objects.all()):
    e_start = 0
    num = 0
    select = ''
    for title in all_titles:
        if title.is_root_node():
            num = 0
            e_start += 1
        select += '<option value="{}">{}{}_({})、{}</option>'.format(title.id, "&nbsp;" * num, str(e_start), str(num//5+1), title.name.strip("*"))
        if title.get_children():
            # 如果该节点有子节点，则再次进行递归
            num += 5
            title_select(title.get_children())
    return select
