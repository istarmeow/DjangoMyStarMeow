from django.utils.safestring import mark_safe
from django import template


register = template.Library()


@register.simple_tag
def active_all(current_url, index):
    """
    获取当前url， course-1-1-2.html
    :param current_url:
    :param index:
    :return:
    """
    url_part_list = current_url.split('-')
    if index == 3:
        if url_part_list[index] == '0.html':
            temp = '<a href="%s" class="active">【全部】</a>'
        else:
            temp = '<a href="%s"">全部</a>'

        url_part_list[index] = '0.html'
    else:
        if url_part_list[index] == '0':
            temp = '<a href="%s" class="active">【全部】</a>'
        else:
            temp = '<a href="%s"">全部</a>'

        url_part_list[index] = '0'

    url_str = '-'.join(url_part_list)

    temp = temp % (url_str, )
    return mark_safe(temp)


@register.simple_tag
def active(current_url, item, index):
    """
    course-0-0-1.html
    :param current_url:
    :param item:
    :param index:
    :return:
    """
    # print('\n当前访问地址：', current_url, item, index, type(index))
    url_part_list = current_url.split('-')
    # print(url_part_list)  # ['/test/course', '0', '0', '0.html']
    if index == 3:
        if str(item['id']) == url_part_list[3].split('.')[0]:  # 如果当前标签被选中
            temp = '<a href="%s" class="active">【%s】</a>'
        else:
            temp = '<a href="%s"">%s</a>'

        url_part_list[index] = str(item['id']) + '.html'  # 拼接对应位置的url

    else:
        if str(item['id']) == url_part_list[index]:
            temp = '<a href="%s" class="active">【%s】</a>'
        else:
            temp = '<a href="%s">%s</a>'

        url_part_list[index] = str(item['id'])

    url_str = '-'.join(url_part_list)  # 拼接整体url
    # print(url_str)
    temp = temp % (url_str, item['name'])  # 生成对应的a标签
    return mark_safe(temp)