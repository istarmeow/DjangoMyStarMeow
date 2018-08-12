from django.shortcuts import render, HttpResponse
from django.views.generic.base import View
from django.shortcuts import redirect, reverse
from .models import Tag, TitleTree, WiKiContent, WiKiContentImage, WiKiComment, ThemeSetting
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from .forms import WiKiCommentForm, ThemeSettingForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.exceptions import PermissionDenied
from django.conf import settings  # next_url=settings.LOGIN_URL

from django.core import serializers

from mptt.exceptions import InvalidMove
from account.models import UserProfile

# 异步任务增加访问量
from .tasks import increase_views, send_comment_mail, create_author_log, create_comments_log

# 将base64字符串还原成图片保存
import base64
# 上传文件保存时间
import datetime
import re
import os
# 使用redis cache
from django.core.cache import cache
# 方法一，使用django_redis，首先需要安装pip install django_redis
from django_redis import get_redis_connection
redis_conn = get_redis_connection('keywords_db')
# 方法二，使用redis，db参数为数据库的序号表示第一个
import redis
redis_strict = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# 自定义权限
from DjangoMyStarMeow.permission import permission_forbidden


def get_group_url_list(url):
    """
    将访问的url存储在列表中，用于前端判断
    EVENT_MENU_GROUP : 事件菜单组
    OTHER_MENU_GROUP : 其他菜单组
    :param url:
    :return:
    """
    group_url_list = list()
    group_url_list.append(url)
    return group_url_list


class TagView(View):
    def get(self, request):
        current_url = reverse('wiki:tags')
        wiki_backend_url_list = get_group_url_list(current_url)

        tags = Tag.objects.all()
        return render(request, 'backend/wiki-tag.html',
                      {
                          'tags': tags,
                          'WIKI_MENU_GROUP': wiki_backend_url_list,
                      })


def add_tag(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        print(name)
        if len(name) == 0:
            return HttpResponse('{"valid_status": "fail", "msg": "名称不能为空"}', content_type='application/json')
        elif len(name) > 10:
            return HttpResponse('{"valid_status": "fail", "msg": "名称不能超过5字"}', content_type='application/json')
        else:
            if not Tag.objects.filter(name=name):
                Tag.objects.create(name=name)
                return HttpResponse('{"valid_status": "success"}', content_type='application/json')
            return HttpResponse('{"valid_status": "fail", "msg": "标签已存在"}', content_type='application/json')


def del_tag(request, tag_id):
    tag = Tag.objects.filter(id=tag_id).delete()
    return redirect(reverse('wiki:tags'))


def update_tag(request):
    tag_id = request.POST.get('tag_id')
    tag_name = request.POST.get('tag_name')
    tag_new_name = request.POST.get('tag_new_name')
    print(tag_id, tag_name, tag_new_name)
    tag = Tag.objects.get(id=tag_id, name=tag_name)
    tag.name = tag_new_name
    tag.save()
    return redirect(reverse('wiki:tags'))


@permission_forbidden(http_exception=403)
def wiki_backend(request):
    # print(reverse('account:login'))
    current_url = reverse('wiki:wiki_backend')
    wiki_backend_url_list = get_group_url_list(current_url)

    keywords = request.GET.get('keywords')
    titles = TitleTree.objects.all()
    if keywords:
        # content_ids = list(c.title.id for c in WiKiContent.objects.filter(content__icontains=str(keywords)))
        # print(content_ids)
        titles = titles.filter(Q(name__icontains=keywords))  # 只搜索标题，如果所有正文包含该字符串的会报错
    # print(titles)
    return render(request, 'backend/wiki-detail.html',
                  {
                      'titles': titles,
                      'WIKI_MENU_GROUP': wiki_backend_url_list,
                      'keywords': keywords,
                  })


# WiKi后端系统，展示标题树、正文和回复
# @permission_forbidden(http_exception=403)  # 可以直接在url上装饰
def wiki_content_backend(request, title_id):
    current_url = reverse('wiki:wiki_content_backend', kwargs={'title_id': title_id})
    wiki_backend_url_list = get_group_url_list(current_url)

    wiki_content = ''
    wiki_comments = ''
    wiki_title = get_object_or_404(TitleTree, id=title_id)

    if WiKiContent.objects.filter(title__id=title_id):
        show_content = True
        # wiki_content = WiKiContent.objects.get(title__id=title_id)
        wiki_content = get_object_or_404(WiKiContent, title__id=title_id)
        # wiki_content.add_views()  # 不计算访问次数
        # wiki_content.save()

        wiki_comments = wiki_content.wiki_comments.all()
        # 显示该文章的评论
        if wiki_comments:
            show_comment = True
        else:
            show_comment = False
        # print(wiki_comments)
    else:
        show_content = False
        show_comment = False

    titles = TitleTree.objects.all()
    return render(request, 'backend/wiki-detail.html',
                  {
                      'titles': titles,
                      'wiki_content': wiki_content,
                      'show_content': show_content,
                      'title_id': title_id,
                      'wiki_title': wiki_title,
                      'WIKI_MENU_GROUP': wiki_backend_url_list,
                      'current_url': current_url,
                      'show_comment': show_comment,
                      'wiki_comments': wiki_comments,
                  })


# WiKi更新及创建视图
class WiKiContentEdit(View):
    @method_decorator(login_required(login_url='/account/login/?next=/wiki/wiki_backend/'))
    def get(self, request, title_id):
        current_url = reverse('wiki:wiki_edit', kwargs={'title_id': title_id})
        wiki_backend_url_list = get_group_url_list(current_url)

        wiki_content = ''
        wiki_title = get_object_or_404(TitleTree, id=title_id)

        if WiKiContent.objects.filter(title__id=title_id):
            show_content = True
            wiki_content = WiKiContent.objects.get(title__id=title_id)
        else:
            show_content = False

        titles = TitleTree.objects.all()
        tags = Tag.objects.all()

        # 推荐星级转换为列表
        star_list = list(map(lambda x: {'num': x[0], 'mean': x[1]}, WiKiContent.STAR))
        return render(request, 'backend/wiki-edit.html',
                      {
                          'titles': titles,
                          'tags': tags,
                          'wiki_content': wiki_content,
                          'show_content': show_content,
                          'title_id': title_id,
                          'wiki_title': wiki_title,
                          'WIKI_MENU_GROUP': wiki_backend_url_list,
                          'star_list': star_list,
                      })

    @method_decorator(login_required(login_url='/account/login/?next=/wiki/wiki_backend/'))
    def post(self, request, title_id):
        title_new = request.POST.get('title_new')
        content = request.POST.get('content')
        recommend = request.POST.get('recommend')
        author_message = request.POST.get('author_message')
        # print(title_new)
        wiki_title = get_object_or_404(TitleTree, id=title_id)
        wiki_title.name = title_new
        wiki_title.save()
        # print(wiki_title)
        tags_new = request.POST.getlist('tags')
        tags_new = Tag.objects.filter(id__in=tags_new)
        # print(tags_new)
        if WiKiContent.objects.filter(title__id=title_id):
            wiki_content = WiKiContent.objects.get(title__id=title_id)
            wiki_content.title = wiki_title
            wiki_content.content = content
            wiki_content.tags = tags_new
            wiki_content.recommend = int(recommend)
            wiki_content.author_message = author_message
            wiki_content.updated_user = request.user
            wiki_content.save()

            # 分布任务更新日志
            create_author_log.delay('update', title_new, title_id)

        else:
            # print('文章不存在，新建')
            wiki_content = WiKiContent.objects.create(
                title=wiki_title,
                content=content,
                recommend=int(recommend),
                author_message=author_message,
                # tags=tags_new,  # 直接在这儿使用会报错
                created_user=request.user,
            )
            wiki_content.tags = tags_new
            wiki_content.save()

            # 分布任务创建日志
            create_author_log.delay('create', title_new, title_id)

        return redirect(reverse("wiki:wiki_content_backend", kwargs={'title_id': title_id}))


# 添加标题
def add_title(request):
    node_id = request.POST.get('node_id', None)
    new_title = request.POST.get('new_title', None)
    is_root_node = request.POST.get('is_root_node', None)
    is_add_child = request.POST.get('is_add_child', None)
    print(node_id, new_title, is_root_node, type(is_root_node), is_add_child, type(is_add_child))

    if is_root_node == 'True':
        if int(is_add_child) == 1:
            # 添加子文档
            try:
                TitleTree.objects.create(name=new_title, parent=TitleTree.objects.get(id=node_id))
            except IntegrityError as IE:
                print(IE)
        else:
            # 添加根文档
            print('添加根文档')
            try:
                TitleTree.objects.create(name=new_title)
            except IntegrityError as IE:
                print(IE)
    else:
        # 如果不是根节点，则只能添加子文档
        # 添加子文档
        try:
            TitleTree.objects.create(name=new_title, parent=TitleTree.objects.get(id=node_id))
        except IntegrityError as IE:
            print(IE)

    return redirect(reverse("wiki:wiki_content_backend", kwargs={'title_id': node_id}))


def del_title(request):
    node_id = request.GET.get('node_id', None)
    try:
        del_title = TitleTree.objects.get(id=node_id)
        if not del_title.name.startswith('*'):

            # 分布任务删除文章日志
            create_author_log.delay('delete', del_title.name, node_id)

            del_title.delete()

    except TitleTree.DoesNotExist:
        pass
    return redirect(reverse("wiki:wiki_content_backend", kwargs={'title_id': TitleTree.objects.first().id}))


def wiki_list(request, *args, **kwargs):
    # print(args, kwargs)
    all_wiki_title = TitleTree.objects.all()
    all_wiki_title_order_by_time = all_wiki_title.filter(wiki_content__isnull=False).order_by('-updated_time')  # 以更新时间排序，这个情况就要判断该标题是否有对应的正文
    all_wiki_title_order_by_views = all_wiki_title.order_by('-wiki_content__views')  # 以文章点击数从大到小排序
    # print(all_wiki_title_order_by_views)

    # 全局搜索，在根节点下，搜索所有，在非根节点下，搜索该子节点
    keywords = request.GET.get('keywords', '').strip()

    if keywords:
        # 方法一：首先需要引入django_redis
        # redis_conn.zincrby('keywords', keywords.lower(), amount=1)
        # 方法而
        redis_strict.zincrby('keywords', keywords.lower(), amount=1)

    # 判断是否为非根目录下
    title_id = kwargs.get('title_id', None)
    # print(title_id)
    current_title = None
    if title_id:
        # 如果不是根标题，则显示他的所有子标题
        current_title = get_object_or_404(TitleTree, id=title_id)
        sub_titles = current_title.get_children()
        if keywords:
            # 如果有搜索关键字，在子页面下，则在当前标题下搜索关键字
            sub_titles = sub_titles.filter(Q(name__icontains=keywords) | Q(wiki_content__content__icontains=keywords))
        show_home = False
        current_url = reverse('wiki:wiki_list', kwargs={'title_id': title_id})
    else:
        sub_titles = list(title for title in all_wiki_title if title.is_root_node())
        if keywords:
            # 如果有搜索关键字，且在主页下，则搜索所有的文集
            sub_titles = all_wiki_title.filter(Q(name__icontains=keywords) | Q(wiki_content__content__icontains=keywords))
        show_home = True
        current_url = reverse('wiki:wiki_list_index')

    # 添加分页
    page = request.GET.get('page', 1)
    paginator = Paginator(sub_titles, 5)  # paginator是分页对象
    try:
        page_sub_titles = paginator.page(page)
    except PageNotAnInteger:
        page_sub_titles = paginator.page(1)
    except EmptyPage:
        page_sub_titles = paginator.page(paginator.num_pages)

    # print('page=', page, ',   keywords=', keywords)

    return render(request, 'foreend/wiki_list.html',
                  {
                      'all_wiki_title': all_wiki_title,
                      'all_wiki_title_order_by_time': all_wiki_title_order_by_time,
                      'all_wiki_title_order_by_views': all_wiki_title_order_by_views,
                      # 'sub_titles': sub_titles,
                      'sub_titles': page_sub_titles,
                      'current_title': current_title,
                      'show_home': show_home,
                      'current_url': current_url,
                      'page': page,
                      'keywords': keywords,
                  })


def wiki_detail(request, title_id):
    all_wiki_title = TitleTree.objects.all()

    current_title = get_object_or_404(TitleTree, id=title_id)
    sub_titles = current_title.get_children()

    # 判断该标题是否对应有内容，如果没有，则不显示正文和评论
    if WiKiContent.objects.filter(title=current_title):
        wiki_content = current_title.wiki_content
        # 增加访问计数
        # wiki_content.add_views()
        # wiki_content.save()
        print("增加[{}]的访问量".format(wiki_content.title.name))
        increase_views.delay(wiki_content.id)
        # increase_views(wiki_content.id)
        # settings.py中设置CELERY_ALWAYS_EAGER = True，上面两条语句效果一样

        wiki_comments = wiki_content.wiki_comments.all()
        other_comments = wiki_comments.filter(parent=None)
        show_wiki = True
    else:
        wiki_content = None
        wiki_comments = None
        other_comments = None
        show_wiki = False

    return render(request, 'foreend/wiki_detail.html',
                  {
                      'all_wiki_title': all_wiki_title,
                      'sub_titles': sub_titles,
                      'current_title': current_title,
                      'wiki_content': wiki_content,
                      'wiki_comments': wiki_comments,
                      'other_comments': other_comments,
                      'show_wiki': show_wiki,
                  })


# @csrf_exempt
def upload_image(request):
    print(request.POST)
    """
    <QueryDict: {'csrfmiddlewaretoken': ['8gtiXSn7Lz0UFrRt9kdN3BPFHMEVvJb75qQchYfb7MfK1PEIJ42tSmBltWlqG8AE', '8gtiXSn7Lz0UFrRt9kdN3BPFHMEVvJb75qQchYfb7MfK1PEIJ42tSmBltWlqG8AE']}>
    """
    print(request.FILES)
    """
    <MultiValueDict: {'editormd-image-file': [<InMemoryUploadedFile: Markdown.png (image/png)>]}>
    """
    image = request.FILES.get('editormd-image-file', None)
    # 将上传的图片绑定到标题，因为它是先创建保存数据库的，如果绑定到正文，则编辑不存在的正文时，会出现模型找不到的情况
    wiki_title = get_object_or_404(TitleTree, id=request.GET.get('wiki_title_id'))

    if image:
        wiki_content_image = WiKiContentImage(
            title=image.name,
            image=image,
            wiki=wiki_title,
            created_user=request.user
        )
        wiki_content_image.save()
        image_url = wiki_content_image.image.url

        res = {
            'success': 1,
            'message': '图片上传成功',
            'url': image_url
        }
    else:
        res = {
            'success': 0,
            'message': '图片上传失败',
        }
    return HttpResponse(json.dumps(res), content_type="text/html")
    # 会出错Resource interpreted as Document but transferred with MIME type application/json
    # return HttpResponse(json.dumps(res), content_type="application/json")


# 用户评论文章，以及作者评论他人的留言
class AddWiKiComment(View):
    @method_decorator(login_required(login_url='/account/login/?next=/wiki/wiki_list/'))
    def post(self, request):
        wiki_comment_form = WiKiCommentForm(request.POST)
        # print(wiki_comment_form)
        if wiki_comment_form.is_valid():
            wiki_comment = wiki_comment_form.save(commit=False)
            wiki_comment.created_user = request.user
            wiki_comment.wiki = get_object_or_404(WiKiContent, id=request.POST.get('wiki_content_id', None))

            if request.POST.get('wiki_comment_id'):
                # 如果是回复别人的评论，则需要保存父节点
                wiki_comment.parent = get_object_or_404(WiKiComment, id=request.POST.get('wiki_comment_id'))
            wiki_comment.save()

            # 异步创建评论日志
            if request.POST.get('wiki_comment_id'):
                # 回复别人的评论
                create_comments_log.delay(request.user.username, 'reply', wiki_comment.wiki.title.name, wiki_comment.wiki.title.id, wiki_comment.content)
            else:
                # 用户评论
                create_comments_log.delay(request.user.username, 'create', wiki_comment.wiki.title.name,  wiki_comment.wiki.title.id, wiki_comment.content)

            # 如果是其他人评论文章，则调用异步任务发送邮件通知
            if not request.POST.get('wiki_comment_id'):
                # print('用户评论发送邮件通知')
                sbj = "用户 {} 在《{}》留言啦！".format(request.user, wiki_comment.wiki.title.name)
                msg = """
                <html>
                    <body>
                    <h1>用户 {} 在文章《{}》留言，请尽快回复哦~</h1>
                    <p>内容：{}</p>
                    </body>
                </html>
                """.format(request.user, wiki_comment.wiki.title.name, wiki_comment.content)
                if settings.SEND_MAIL_CONFIG:
                    # 异步发送邮件
                    send_comment_mail.delay(sbj, msg)

            return HttpResponse('{"valid_status": "success"}', content_type='application/json')
        else:
            # print(wiki_content_form.errors)
            info = {"valid_status": "fail", "msg": wiki_comment_form.errors}
            s = json.dumps(info, ensure_ascii=False)  # ensure_ascii=False中文不乱码
            print(s, type(s))
            return HttpResponse(s, content_type='application/json')


# 后台删除评论
def del_comment(request):
    comment_id = request.GET.get('comment_id', '')
    if WiKiComment.objects.filter(id=comment_id):
        wiki_comment = WiKiComment.objects.get(id=comment_id)
        wiki_comment.delete()
        res = {'msg': '已删除'}

        # 异步记录删除评论
        create_comments_log.delay(wiki_comment.created_user.username, 'delete', wiki_comment.wiki.title.name, wiki_comment.wiki.title.id, wiki_comment.content)

    else:
        res = {'msg': '删除失败'}

    return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')


# 移动标题，结束后跳转回主页，失败则不做其他操作
def move_title(request):
    current_title = request.POST.get('current_title', '')
    current_title = TitleTree.objects.get(id=current_title)
    target = request.POST.get('target', '')
    if int(target) == 0:
        target = None
    else:
        target = TitleTree.objects.get(id=target)
    position = request.POST.get('position', '')
    # print(target, position)

    try:
        current_title.move_to(target, position)

        # 分布任务移动日志
        if target:
            create_author_log.delay('move', current_title.name, current_title.id, target.name)
        else:
            create_author_log.delay('move', current_title.name, current_title.id, '根目录')

    except InvalidMove:
        pass

    return redirect(reverse('wiki:wiki_backend'))


# 更改主题并记录到数据库
def change_theme(request):
    if request.method == 'POST':
        if request.user.is_authenticated():
            # print(request.user)
            theme_id = request.POST.get('theme_id')
            theme = ThemeSetting.objects.get(id=theme_id)
            # 如果用户没有user_profile则会报错，先判断是否存在，如不不存在，则进行新建
            if not UserProfile.objects.filter(user=request.user):
                UserProfile.objects.create(user=request.user)
            request.user.user_profile.theme = theme
            request.user.user_profile.save()
            msg = {'submit_info': '【{}】主题已设置成功'.format(theme.name)}
        else:
            msg = {'submit_info': '用户未登录'}
        return HttpResponse(json.dumps(msg))
    else:
        theme = ThemeSetting.objects.all()
        theme_id = request.GET.get('theme_id', '')
        if theme_id:
            theme = theme.filter(id=theme_id)
        theme_to_json = serializers.serialize('json', theme)
        return HttpResponse(theme_to_json)


# 使用ctrl+v粘贴图片功能，已实现
def upload_paste_image(request):
    base64data = request.POST.get('base64data')
    title_id = request.GET.get('title_id')
    # print('正在上传图片', datetime.datetime.now())

    # print(base64data)  # data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHMAAA
    if base64data:
        wiki_title = get_object_or_404(TitleTree, id=title_id)
        image_title = 'ID_{}_{}'.format(title_id, str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
        # 获取图片类型
        pattern = re.compile(r'.*image/(.+);base64,')
        # print('获取图片类型', datetime.datetime.now())
        image_type = pattern.match(base64data).group(1)
        image_name = '{}.{}'.format(image_title, image_type)  # 名字为xxx.png格式

        # 终于解决保存图片不正常的问题了，要去掉前缀data:image...base64,  !!!
        # print('去掉base64字符串前缀', datetime.datetime.now())
        base64data = re.sub(pattern, '', base64data, count=1)  # 去掉base64字符串的前缀，这种方式如果图片大，时间成本太高了，所以要指明替换次数count
        # base64data = base64data.split('base64,', 1)[1]  # 第二种方式，字符串分割，规定匹配次数为1，则只分割为2段，否则字符串太长时间成本高

        # 报错binascii.Error: Incorrect padding解决方案，对base64解码的string补齐等号
        # print('补齐base64字符串等号', datetime.datetime.now())
        missing_padding = 4 - len(base64data) % 4
        if missing_padding:
            base64data += '=' * missing_padding

        # print(type(base64data))  # <class 'str'>
        # print('解码中', datetime.datetime.now())
        image_data = base64.b64decode(base64data)  # 把二进制文件解码，并赋值给image_data
        # print(type(image_data))  # <class 'bytes'>

        # 保存图片到目标位置
        image_save_path = os.path.join(settings.MEDIA_ROOT, str(datetime.datetime.now().strftime("images/wiki/%Y/%m")), image_name)  # media路径、临时文件路径、文件名
        # print('正在保存图片到文件', datetime.datetime.now())
        with open(image_save_path, 'wb') as image_file:
            image_file.write(image_data)

        # 图片路径，用于模板上直接访问的地址
        image_url = os.path.join(str(datetime.datetime.now().strftime("images/wiki/%Y/%m")), image_name).replace('\\', '/')

        # print('保存图片到数据库', datetime.datetime.now())
        # 保存文件到数据库，图片路径为数据库的格式	images/wiki/2018/07/ID_42_20180710_220259.png
        WiKiContentImage.objects.create(
            wiki=wiki_title,
            title=image_title,
            image=image_url,
            created_user=request.user,
        )
        res = "![{}]({} '{}')".format(wiki_title.name, os.path.join(settings.MEDIA_URL, image_url), wiki_title.name+'>'+image_title)
        return HttpResponse(res)
    else:
        return HttpResponse('图片上传失败')


# 主题设置
def theme_setting(request):
    themes = ThemeSetting.objects.all()
    if request.method == 'POST':
        theme_setting_form = ThemeSettingForm(request.POST, request.FILES)
        if theme_setting_form.is_valid():
            theme_setting_form.save()
    else:
        theme_setting_form = ThemeSettingForm()

    return render(request, 'backend/wiki-theme.html',
                  {
                      'theme_setting_form': theme_setting_form,
                      'themes': themes,
                  })


# 删除主题
def delete_theme(request):
    delete_id = request.GET.get('delete_id')
    ThemeSetting.objects.filter(id=delete_id).delete()
    res = {'del_msg': '成功删除主题'}
    return HttpResponse(json.dumps(res))


# 显示搜索历史
def history_search(request):
    # res = [str(i) for i in range(5)]
    keywords = request.GET.get('keywords', '').strip()

    # 方法一
    # 获取添加的值，以添加量排序
    l1 = redis_conn.zrevrange('keywords', 0, 8, withscores=True)
    # print(l1)  # [(b'django', 4.0), (b'python', 2.0), (b'redis', 1.0)]
    res = redis_conn.zrevrange('keywords', 0, 8)
    # print(res, type(res))  # [ b'django', b'python', b'redis'] <class 'list'>
    res = list(item.decode() for item in res if keywords.lower() in item.decode())  # 将byte类型转换为str类型
    # print(res, type(res))  # ['django', 'python', 'redis'] <class 'list'>

    # 方法二，使用redis直接连接的数据库
    res = redis_strict.zrevrange('keywords', 0, 8)
    res = list(item for item in res if keywords.lower() in item)
    return HttpResponse(json.dumps(res))


# 删除历史搜索记录
@permission_forbidden(http_exception=403)  # 要求管理员权限
def history_search_delete(request):
    redis_keys = redis_strict.keys()
    print(type(redis_keys))  # <class 'list'>
    if 'keywords' in redis_keys:
        redis_strict.delete('keywords')
        return HttpResponse('success')
    return HttpResponse('fail or other')

