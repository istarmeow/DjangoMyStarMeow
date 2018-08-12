from django.utils.safestring import mark_safe
from django import template


register = template.Library()


@register.simple_tag
def active_all(request_path, index):
    url_part_list = request_path.split('-')
    # print(url_part_list)
    # ['/event', '0', '0', '0', '0', '0.html']
    # 第五组带.html，需要分开判断

    if url_part_list[index] == '0' or url_part_list[index] == '0.html':
        temp = '''
        <li class="nav-item">
            <a class="nav-link active" href="{href}">全部</a>
        </li>
        '''
    else:
        temp = '''
        <li class="nav-item">
            <a class="nav-link" href="{href}">全部</a>
        </li>
        '''

    if index != 5:
        url_part_list[index] = '0'
    else:
        url_part_list[index] = '0.html'

    href = '-'.join(url_part_list)
    return mark_safe(temp.format(href=href))


@register.simple_tag
def active(request_path, item, index):
    url_part_list = request_path.split('-')
    # 下面判断中，前面表示 event-0-1-5-1-，后面表示 3.html
    if url_part_list[index] == str(item['id']) or url_part_list[index] == str(item['id']) + '.html':
        temp = '''
        <li class="nav-item">
            <a href="{href}" class="nav-link active">{name}</a>
        </li>
        '''
    else:
        temp = '''
        <li class="nav-item">
            <a href="{href}" class="nav-link">{name}</a>
        </li>        
        '''
    if index == 5:
        # 第五组有后缀.html，需单独处理
        url_part_list[index] = str(item['id']) + '.html'
    else:
        url_part_list[index] = str(item['id'])
    href = '-'.join(url_part_list)

    if index == 1:
        """
        event-1-0-0-0-0.html
        event-2-0-0-0-0.html
        event-3-0-0-0-0.html
        """
        return mark_safe(temp.format(href=href, name=item['username']))
    if index == 2:
        return mark_safe(temp.format(href=href, name=item['status_tag']))
    if index == 3:
        return mark_safe(temp.format(href=href, name=item['level_tag']))
    if index == 4:
        return mark_safe(temp.format(href=href, name=item['category_name']))
    if index == 5:
        return mark_safe(temp.format(href=href, name=item['project_name']))