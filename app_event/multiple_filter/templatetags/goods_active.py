from django.utils.safestring import mark_safe
from django import template


register = template.Library()


@register.simple_tag
def active_all(current_url, index):
    """
    获取当前url，进行值修改拼接
    :param current_url: http://127.0.0.1:8000/test/goods-0-0-0-0.html
    :param index:
    :return:
    """
    a_href_active = """
    <a href="{href}" class="active">【全部】</a>
    """
    a_href_unactive = """
    <a href="{href}">全部</a>
    """
    url_part_list = current_url.split('-')
    if index == len(url_part_list)-1:  # 最后一个带.html要特殊处理
        if url_part_list[index] == '0.html':
            a_href = a_href_active
        else:
            a_href = a_href_unactive

        url_part_list[index] = '0.html'
    else:
        if url_part_list[index] == '0':
            a_href = a_href_active
        else:
            a_href = a_href_unactive

        url_part_list[index] = '0'

    href = '-'.join(url_part_list)
    a_href = a_href.format(href=href)
    return mark_safe(a_href)


@register.simple_tag
def active(current_url, item, index):
    """
    获取当前url，进行值修改拼接
    :param current_url: http://127.0.0.1:8000/test/goods-0-0-0-0.html
    :param index:
    :return:
    """
    a_href_active = """
    <a href="{href}" class="active">【{name}】</a>
    """
    a_href_unactive = """
    <a href="{href}">{name}</a>
    """
    url_part_list = current_url.split('-')
    if index == len(url_part_list)-1:  # 最后一个带.html要特殊处理
        if url_part_list[index] == str(item['id']) + '.html':
            a_href = a_href_active
        else:
            a_href = a_href_unactive

        url_part_list[index] = str(item['id']) + '.html'
    else:
        # print(item['id'], type(item['id']))  # item['id']是int类型
        if url_part_list[index] == str(item['id']):
            a_href = a_href_active
        else:
            a_href = a_href_unactive

        url_part_list[index] = str(item['id'])

    href = '-'.join(url_part_list)
    if index in range(1, 4):
        a_href = a_href.format(href=href, name=item['name'])
    if index == len(url_part_list)-1:
        a_href = a_href.format(href=href, name=item['status'])
    return mark_safe(a_href)