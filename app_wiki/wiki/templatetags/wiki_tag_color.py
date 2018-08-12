#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django import template
from wiki.models import ColorType
from random import choice


register = template.Library()


# 随机颜色
@register.simple_tag
def random_color():
    colors = ColorType.objects.all()
    return choice(colors).code


