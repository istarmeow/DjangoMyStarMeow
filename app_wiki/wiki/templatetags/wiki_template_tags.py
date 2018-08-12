from django import template
from wiki.models import ThemeSetting, WiKiContent, TitleTree, AuthorLog, CommentsLog
from django.shortcuts import reverse
import time

register = template.Library()


@register.simple_tag
def remove_title_asterisk(title):
    # 移除标题前面的星号
    if title.startswith('*'):
        return title[1:]
    else:
        return title


@register.simple_tag
def show_star(recommend):
    # 显示作者推荐星级
    heart = '<span class="glyphicon glyphicon-heart"></span>'
    heart_empty = '<span class="glyphicon glyphicon-heart-empty"></span>'
    return recommend * heart + (5-recommend) * heart_empty


@register.simple_tag
def change_theme():
    # 显示主题列表，前端使用js进行切换
    theme_list = ''
    for theme in ThemeSetting.objects.all():
        theme_list += '<span class="badge badge-secondary" onclick="change_theme(\'{}\')">{}</span>&nbsp;'.format(theme.id, theme.name)
    return theme_list


@register.simple_tag
def wiki_content_all_views():
    views_list = list(map(lambda x: x.views, WiKiContent.objects.all()))
    return str(sum(views_list))


@register.simple_tag
def title_list_view(flag, marking, all_titles=TitleTree.objects.all()):
    if int(flag) == 1:
        # 设置一个标识，如果后端更新了值，而all_titles为原来地址空间的值，所以当flag为1时，重新从数据库中获得值，然后再进行遍历，遍历的时候flag为0
        all_titles = TitleTree.objects.all()
    e_start = 0
    num = 0
    select = ''
    for title in all_titles:
        if title.is_root_node():
            num = 0
            e_start += 1
        if marking == 'option':
            # 如果是后端访问，返回的是一个选择
            select += '<option value="{}">{}{}_({})、{}</option>'.format(title.id, "&nbsp;" * num, str(e_start), str(num//5+1), title.name.strip("*"))
        elif marking == 'list':
            # 如果是前端访问，返回的是一个带链接的列表
            select += '<li class="list-group-item"><a href="{}">{}{}_({})、{}</a></li>'.format(reverse('wiki:wiki_detail', args=[str(title.id), ]), "&nbsp;" * num, str(e_start), str(num//5+1), title.name.strip("*"))
        else:
            select += ''

        if title.get_children():
            # 如果该节点有子节点，则再次进行递归
            num += 5
            title_list_view(flag=0, marking=marking, all_titles=title.get_children())
    return select


@register.simple_tag
def show_author_log(nums, flag=1):
    op_ch = dict(AuthorLog.OPERATE_CHOICES)
    res = ''
    for log in AuthorLog.objects.all()[:int(nums)]:
        title_name = log.title_name
        if TitleTree.objects.filter(id=log.title_id):
            title_name = "<a href={}>{}</a>".format(reverse('wiki:wiki_detail', args=[log.title_id, ]), log.title_name)

        create_time = log.created_time.strftime("%Y-%m-%d %H:%M:%S")

        if log.operate == 'move':
            tmp = "{}  作者 移动了《{}》 到 《{}》".format(create_time, title_name, log.message)
        else:
            tmp = "{}  作者 {} 《{}》".format(create_time, op_ch[str(log.operate)], title_name)
        if flag == 1:
            res += '<div class="well">{}</div>'.format(tmp)
        elif flag == 0:
            res += '<li class="m-t-xs"">{}</li>'.format(tmp)
    return res


@register.simple_tag
def show_comments_log(nums, flag=1):
    """
    xxx 评论了 《xxx》：xxx
    作者 回复了 xxx关于《xxx》的评论：xxx
    作者 删除了 xxx关于《xxx》的评论：xxx
    """
    op_ch = dict(CommentsLog.OPERATE_CHOICES)
    res = ''
    for log in CommentsLog.objects.all()[:int(nums)]:
        title_name = log.title_name
        if TitleTree.objects.filter(id=log.title_id):
            title_name = '<a href="{}">{}</a>'.format(reverse('wiki:wiki_detail', args=[log.title_id, ]), log.title_name)

        created_time = log.created_time.strftime("%Y-%m-%d %H:%M:%S")

        if log.operate == 'create':
            tmp = "{}   <b>{}</b> 评论了 《{}》：{}".format(created_time, log.user_name, title_name, log.content)
        else:
            tmp = "{}   作者 {} <b>{}</b> 关于 《{}》 的评论：{}".format(created_time, op_ch[str(log.operate)], log.user_name, title_name, log.content)

        if flag == 1:
            res += '<div class="well">{}</div>'.format(tmp)
        elif flag == 0:
            res += '<li class="list-group-item">{}</li>'.format(tmp)
    return res
