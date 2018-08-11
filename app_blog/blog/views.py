from django.shortcuts import render, HttpResponse, redirect
from .models import Tag, Category, Article, BlogImage, BlogNotice
from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView, View
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
import random
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.urls import reverse_lazy
from .forms import ArticleForm, BlogNoticeForm, CategoryForm, TagForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
import datetime
import random
import re
import os
import base64
from django.conf import settings
from comment.models import BlogComment
import time


# 定义在前面，如果有更新，统计可能不会改变
# categories = Category.objects.all()  # 获取全部的分类对象
# categories = Category.objects.annotate(num_posts=Count('articles')).all()  # 获取不是草稿的分类对象，并统计各分类的数量
# tags = Tag.objects.all()  # 获取全部的标签对象
# tags = Tag.objects.annotate(blog_nums=Count('articles')).all()  # 获取标签并计算博客数量
# year_months = Article.objects.datetimes('publish_time', 'month', order='DESC')


class BlogList(ListView):
    model = Article  # 模板中使用object_list表示所有blog对象，等价于Article.objects.all()

    # 自定义的模板名称，如果定义在url中，可以实现同一个视图返回返回不同的模板
    template_name = 'blog-list.html'  # 指定模板名字，如果不定义默认是article-list.html

    # 制作“友好”模板上下文
    context_object_name = 'blog_list'  # 即在模板中可以使用blog_list表示所有对象，当然object_list也可以用

    # 查看对象的子集-添加过滤条件
    queryset = Article.objects.all()  # 直接使用模型中定义的PublishedManager模型管理器，等价于queryset = Article.objects.filter(status='published')

    paginate_by = 12  # 分页实现，在模板中就需要使用page_obj值来使用分页对象

    # 动态过滤-根据分类过滤列表，如果不使用这个函数，默认使用queryset的结果
    def get_queryset(self):
        self.choose_category = None
        self.access_flag = ''
        self.keywords = ''
        self.published = self.queryset.filter(status='published')
        self.draft = self.queryset.filter(status='draft')

        if self.kwargs.get('category_id'):
            # 如果给了分类，则筛选分类的结果
            self.choose_category = get_object_or_404(Category, id=self.kwargs['category_id'])
            self.access_flag = '分类归档【{}】'.format(self.choose_category.name)
            return self.published.filter(category=self.choose_category)
        elif self.kwargs.get('year') and self.kwargs.get('month'):
            # 如果给了年月日期，则进行按月归档
            self.access_flag = '按月归档【{}年{}月】'.format(self.kwargs['year'], self.kwargs['month'])
            return self.published.filter(publish_time__year=self.kwargs['year'], publish_time__month=self.kwargs['month'])
        elif self.kwargs.get('tag_id'):
            # 按标签进行搜索
            self.choose_tag = get_object_or_404(Tag, id=self.kwargs['tag_id'])
            self.access_flag = '标签归档【{}】'.format(self.choose_tag.name)
            return self.choose_tag.articles.filter(status='published')
        elif self.request.path == reverse('blog:blog_list_search') or self.request.path == reverse('blog:blog_list_search_public'):
            # 全局搜索字符串，当访问的链接是搜索url时
            # self.keywords = self.kwargs['keywords']
            self.keywords = self.request.GET.get('keywords', '').strip()
            print(self.keywords)
            self.access_flag = '搜索字符【{}】'.format(self.keywords)
            return self.published.filter(Q(title__icontains=self.keywords) | Q(content__icontains=self.keywords))
        elif self.request.path == reverse('blog:blog_draft'):
            return self.draft
        else:
            # 直接给出已发布的列表，在获得查询集使用
            return self.queryset

    # 添加额外的上下文
    def get_context_data(self, **kwargs):
        # 传递到模板的变量-上下文数据
        context = super(BlogList, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(num_posts=Count('articles')).all()  # 获取不是草稿的分类对象，并统计各分类的数量
        context['tags'] = Tag.objects.annotate(blog_nums=Count('articles')).all()  # 获取标签并计算博客数量
        context['published_nums'] = self.published.count()
        context['draft_nums'] = self.draft.count()
        context['recent_blog'] = self.published.order_by('-publish_time')[:3]  # 最近发布的博客
        context['hot_blog'] = self.published.order_by('-views')[:3]  # 点击量最多博客
        context['year_months'] = self.published.datetimes('publish_time', 'month', order='DESC')  # 按月归档
        context['random_blog'] = random.sample(list(self.published), 3)  # 随机推荐三篇博客
        context['most_comment_blog'] = self.published.annotate(most_comment=Count('comments')).order_by('-most_comment', '-publish_time')[:3]
        context['choose_category'] = self.choose_category  # 将选择分类添加到上下文中，这样才可以在模板中使用
        context['access_flag'] = self.access_flag  # 归档的标识
        context['num_comment'] = BlogComment.objects.filter(parent=None).count()  # 处于根节点的评论
        context['num_other_comment'] = BlogComment.objects.exclude(parent=None).count()  # 非根节点的其他评论
        context['num_words'] = sum(list(len(article.content) for article in self.published.all()))  # 统计所有博客字数
        context['notice'] = BlogNotice.objects.first()  # 公告实例
        context['keywords'] = self.keywords
        return context


class BlogDetail(DetailView):
    model = Article
    template_name = 'blog-detail.html'
    context_object_name = 'blog_article'
    pk_url_kwarg = 'article_id'  # 如果没声明这个值，url只能使用pk：article/(?P<pk>\d+)/detail/，现在可以使用：article/(?P<article_id>\d+)/detail/

    # 用来获取对象的方法
    def get_object(self, queryset=None):
        # 返回该视图要显示的对象。 如果提供了queryset，该查询将被用作对象的源；否则将使用get_queryset()
        obj = super(BlogDetail, self).get_object()

        # 获取该博客的最顶级评论，并赋值给comment_all，模板可以通过这个进行调用
        obj.comment_all = obj.comments.filter(parent=None).order_by('-created_time')

        if obj.status == 'published':
            # 设置浏览量增加时间判断,同一篇文章两次浏览超过半小时才重新统计阅览量
            session = self.request.session
            browse_blog_time = 'browse_blog_{}'.format(obj.id)
            last_browse_time = session.get(browse_blog_time)
            if not last_browse_time:
                # 如果session中还没有browse_blog_xx这个键，则增加一次访问量，并设置它的值为当前时间
                obj.viewed()  # 调用浏览量+1的函数
                session[browse_blog_time] = time.time()
            else:
                if time.time() - last_browse_time > 60 * 30:
                    obj.viewed()  # 调用浏览量+1的函数
                    session[browse_blog_time] = time.time()
            return obj
        elif obj.status == 'draft':
            # 如果访问的是草稿，假如当前用户是超级用户，则显示该文章，否则，显示其他提示内容
            if self.request.user.is_superuser:
                return obj
            else:
                obj.title += '-【草稿】'
                obj.content = '### 作者还未发布该文章，请稍候再来看看哦'
            return obj
        else:
            return obj

    # 自定义函数，用来返回相似的博客，self.object代表当前的博客
    def get_similar_blog(self):
        blog_tags_ids = self.object.tags.values_list('id', flat=True)  # 但会当前博客所有标签的id
        similar_blog = Article.published.filter(tags__in=blog_tags_ids).exclude(id=self.object.id)  # 获取包含这些标签的博客并排除当前博客
        similar_blog = similar_blog.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish_time')[:5]  # 使用Count聚合函数来生成一个计算字段same_tags
        return similar_blog

    def get_context_data(self, **kwargs):
        context = super(BlogDetail, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(num_posts=Count('articles')).all()  # 获取不是草稿的分类对象，并统计各分类的数量
        context['draft_nums'] = Article.draft.count()
        context['similar_blog'] = self.get_similar_blog()
        context['num_comment'] = BlogComment.objects.filter(blog=self.object, parent=None).count()  # 处于根节点的评论
        context['num_other_comment'] = BlogComment.objects.filter(blog=self.object).exclude(parent=None).count()  # 非根节点的其他评论
        return context


class BlogDelete(DeleteView):
    model = Article
    pk_url_kwarg = 'article_id'  # 如果没有则使用默认的pk在url里面
    context_object_name = 'blog_article'
    template_name = 'blog-confirm-delete.html'  # 如果不定义则会使用article_confirm_delete.html，模板中需要定义post确认删除
    success_url = reverse_lazy('blog:blog_list')


@method_decorator(login_required, name='dispatch')
class BlogCreate(CreateView):
    model = Article
    template_name = 'blog-edit.html'
    form_class = ArticleForm
    # success_url = 'xxx'  # 可以设置创建成功后跳转地址，也可以使用下面的函数

    def get_success_url(self):
        # print(self.object.id)  # 可以得到新创建的博客id
        # return reverse('blog:blog_list')
        return reverse('blog:blog_detail', kwargs={'article_id': self.object.id})

    # 表单验证通过，修改一些字段的值
    def form_valid(self, form):
        if self.request.user:
            form.instance.author = self.request.user
        return super(BlogCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(BlogCreate, self).get_context_data(**kwargs)
        context['status_choices'] = list(map(lambda x: {'status_code': x[0], 'status_value': x[1]}, Article.STATUS_CHOICES))
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        return context


# 粘贴从editor.md输入框中上传的图片
def upload_paste_image(request):
    print('正在上传粘贴的图片')
    base64data = request.POST.get('base64data')
    now = datetime.datetime.now()
    image_type_list = ["jpg", "jpeg", "gif", "png", "bmp", "webp"]

    if base64data:
        image_title = "BLOG_{}_{}".format(str(now.strftime("%Y%m%d_%H%M%S")), random.randint(10, 99))
        # 获取图片类型
        pattern = re.compile(r'.*image/(.+);base64,')
        image_type = pattern.match(base64data).group(1).lower()
        if image_type in image_type_list:
            image_name = '{}.{}'.format(image_title, image_type)  # 名字为xxx.png格式

            # 去掉base64字符串前缀
            base64data = re.sub(pattern, '', base64data, count=1)

            # 补齐base64字符串等号
            missing_padding = 4 - len(base64data) % 4
            if missing_padding:
                base64data += '=' * missing_padding

            # 把二进制文件解码，并赋值给image_data
            image_data = base64.b64decode(base64data)

            # 保存图片到目标位置
            image_save_path = os.path.join(settings.MEDIA_ROOT, str(datetime.datetime.now().strftime("images/blog/%Y/%m")), image_name)  # media路径、临时文件路径、文件名

            # 保存图片
            with open(image_save_path, 'wb') as image_file:
                image_file.write(image_data)

            # 获取文件的大小
            image_size = round(os.path.getsize(image_save_path)/float(1024), 2)

            # 图片路径，用于模板上直接访问的地址
            image_url = os.path.join(str(now.strftime("images/blog/%Y/%m")), image_name).replace('\\', '/')

            # 保存图片到数据库，images/blog/2018/07/python入门.png
            BlogImage.objects.create(
                title=image_title,
                image=image_url,
                extension=image_type,
                size=image_size,
                created_user=request.user
            )

            res = {
                'upload_status': True,
                'upload_info': '图片上传成功',
                'image_url_md': "![{}]({} '{}')".format(image_title, os.path.join(settings.MEDIA_URL, image_url), '博客图集'+image_name)
            }
        else:
            res = {
                'upload_status': False,
                'upload_info': '图片上传失败，{}不是要求的格式'.format(image_type),
            }
    else:
        res = {
            'upload_status': False,
            'upload_info': '未正确获取图片信息',
        }
    return HttpResponse(json.dumps(res))


# 点击editor.md图标上传图片
def upload_image(request):
    image_file = request.FILES.get('editormd-image-file', None)
    now = datetime.datetime.now()
    image_title = "BLOG_{}_{}".format(str(now.strftime("%Y%m%d_%H%M%S")), random.randint(10, 99))
    if image_file:
        # 获取文件大小
        image_size = round(image_file.size/float(1024), 2)  # 转换为kb，并保留两位小数

        # 得到文件名，取其后缀
        image_name = image_file.name
        image_type = image_name.split('.')[1]
        image_name = '{}.{}'.format(image_title, image_type)

        # 保存图片到目标位置
        image_save_path = os.path.join(settings.MEDIA_ROOT, str(datetime.datetime.now().strftime("images/blog/%Y/%m")), image_name)  # media路径、临时文件路径、文件名

        # 手动保存图片
        with open(image_save_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        # 图片路径，用于模板上直接访问的地址
        image_url = os.path.join(str(now.strftime("images/blog/%Y/%m")), image_name).replace('\\', '/')

        # 保存图片到数据库，images/blog/2018/07/python入门.png
        image = BlogImage.objects.create(
            title=image_title,
            image=image_url,  # 如果不使用手动保存，不重命名，可以直接使用image=image_file保存到数据库
            extension=image_type,
            size=image_size,
            created_user=request.user
        )

        res = {
            'success': 1,
            'message': '图片上传成功',
            'url': image.image.url,  # 获取数据库中的图片可访问路径
        }
    else:
        res = {
            'success': 0,
            'message': '图片上传失败',
        }

    return HttpResponse(json.dumps(res))


@method_decorator(login_required, name='dispatch')
class BlogUpdate(UpdateView):
    model = Article
    template_name = 'blog-edit.html'
    form_class = ArticleForm
    context_object_name = 'blog_article'  # 传递给前端的博客对象
    pk_url_kwarg = 'article_id'
    # success_url = 'xxx'  # 可以设置创建成功后跳转地址，也可以使用下面的函数

    def get_success_url(self):
        return reverse('blog:blog_list')

    # 表单验证通过，修改一些字段的值
    def form_valid(self, form):
        if self.request.user:
            form.instance.author = self.request.user
        return super(BlogUpdate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(BlogUpdate, self).get_context_data(**kwargs)
        context['status_choices'] = list(map(lambda x: {'status_code': x[0], 'status_value': x[1]}, Article.STATUS_CHOICES))
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        return context


class BlogNoticeUpdate(UpdateView):
    model = BlogNotice
    template_name = 'blog-notice-edit.html'
    form_class = BlogNoticeForm
    context_object_name = 'blog_notice'
    success_url = reverse_lazy('blog:blog_list')  # 这儿不能使用reverse


# 分类管理
class CategoryManage(View):
    # 汇总需要显示的值，返回一个列表
    @staticmethod
    def get_summary_list():
        categories = Category.objects.annotate(num_blog=Count('articles')).all()  # 获取不是草稿的分类对象，并统计各分类的数量
        summary_list = list()
        for category in categories:
            tmp = dict()
            articles = Article.published.filter(category=category)
            newest_blog = articles.first()  # 获取该分类的最新博客
            most_comment_blog = articles.annotate(most_comment=Count('comments')).order_by('-most_comment').first()  # 评论最多的一条
            hot_blog = articles.order_by('-views').first()
            tmp['newest_blog'] = newest_blog
            tmp['most_comment_blog'] = most_comment_blog
            tmp['hot_blog'] = hot_blog
            tmp['category'] = category
            summary_list.append(tmp)
        return summary_list

    def get(self, request):
        category_form = CategoryForm()  # 分类的表单
        parameter = ''
        button_name = '保存'
        button_style = 'primary'
        info = ''
        update_id = request.GET.get('update')

        if update_id:
            update_category = get_object_or_404(Category, id=update_id)
            category_form.initial['name'] = update_category.name  # 初始化表单的值为需要更新的值
            parameter = '?update={}'.format(update_id)  # 给提交表单的参数
            info = '更新分类【{}】的名称'.format(update_category.name)

        delete_id = request.GET.get('delete')
        if delete_id:
            delete_category = get_object_or_404(Category, id=delete_id)
            category_form.initial['name'] = delete_category.name  # 初始化表单的值为需要更新的值
            parameter = '?delete={}'.format(delete_id)  # 给提交表单的参数
            button_name = '确认'
            button_style = 'danger'
            info = '删除分类【{}】'.format(delete_category.name)

        return render(request, 'blog-manage-category.html',
                      {
                          'summary_list': self.get_summary_list(),
                          'category_form': category_form,
                          'parameter': parameter,
                          'button_name': button_name,
                          'button_style': button_style,
                          'info': info
                      })

    def post(self, request):
        category_form = CategoryForm()
        parameter = ''
        button_name = '保存'
        button_style = 'primary'
        info = ''

        new_name = request.POST.get('name')  # 获取表单中的更新的名称

        # 如果url中存在update参数，则进入更新逻辑
        update_id = request.GET.get('update')
        if update_id:
            # 更新某一个分类
            button_name = '保存'
            button_style = 'primary'
            update_category = get_object_or_404(Category, id=update_id)  # 需要更新的分类实例
            if Category.objects.filter(name=new_name):
                # 如果表单中的更新名称已存在，则进行提示
                category_form.initial['name'] = update_category.name  # 初始化表单的值为需要更新的值
                parameter = '?update={}'.format(update_id)  # 给提交表单的参数
                info = '更新分类【{}】的名称失败，已存在【{}】'.format(update_category.name, new_name)
                return render(request, 'blog-manage-category.html',
                              {
                                  'summary_list': self.get_summary_list(),
                                  'category_form': category_form,
                                  'parameter': parameter,
                                  'button_name': button_name,
                                  'button_style': button_style,
                                  'info': info
                              })
            else:
                # 如果更新名称不存在，则将需要更新的实例name进行赋值保存数据库
                update_category.name = new_name
                update_category.save()
                return redirect(reverse('blog:manage_category'))

        # 如果url中存在delete参数，则进入删除逻辑
        delete_id = request.GET.get('delete')
        if delete_id:
            # 删除一个分类
            delete_category = get_object_or_404(Category, id=delete_id)
            category_form.initial['name'] = delete_category.name  # 初始化表单的值为需要更新的值
            parameter = '?delete={}'.format(delete_id)  # 给提交表单的参数
            button_name = '确认'
            button_style = 'danger'
            info = '删除分类【{}】，分类不为空不支持删除'.format(delete_category.name)
            if delete_category.articles.all():
                return render(request, 'blog-manage-category.html',
                              {
                                  'summary_list': self.get_summary_list(),
                                  'category_form': category_form,
                                  'parameter': parameter,
                                  'button_name': button_name,
                                  'button_style': button_style,
                                  'info': info
                              })
            else:
                print('删除分类【{}】'.format(delete_category.name))
                delete_category.delete()  # 删除分类
                return redirect(reverse('blog:manage_category'))

        # 创建新分类
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return redirect(reverse('blog:manage_category'))
        else:
            print('表单验证不通过')
            return render(request, 'blog-manage-category.html',
                          {
                              'summary_list': self.get_summary_list(),
                              'category_form': category_form,
                              'button_name': button_name,
                              'button_style': button_style,
                              'info': info
                          })


# 标签管理
class TagManage(View):
    def get(self, request):
        tag_form = TagForm()
        tags = Tag.objects.annotate(blog_nums=Count('articles')).all()
        parameter = ''
        button_name = '保存'
        button_style = 'primary'
        info = ''

        delete_id = request.GET.get('delete')
        if delete_id:
            delete_tag = get_object_or_404(Tag, id=delete_id)
            tag_form.initial['name'] = delete_tag.name
            parameter = '?delete={}'.format(delete_id)  # 给提交表单的参数
            button_name = '确认'
            button_style = 'danger'
            info = '删除标签【{}】'.format(delete_tag.name)

        return render(request, 'blog-manage-tag.html',
                      {
                          'tag_form': tag_form,
                          'tags': tags,
                          'button_name': button_name,
                          'button_style': button_style,
                          'info': info,
                          'parameter': parameter,
                      })

    def post(self, request):
        tags = Tag.objects.annotate(blog_nums=Count('articles')).all()
        parameter = ''
        button_name = '保存'
        button_style = 'primary'
        info = ''

        delete_id = request.GET.get('delete')
        if delete_id:
            # 删除一个标签
            delete_tag = get_object_or_404(Tag, id=delete_id)
            print('删除分类【{}】'.format(delete_tag.name))
            delete_tag.delete()  # 删除分类
            return redirect(reverse('blog:manage_tag'))

        # 创建新标签
        tag_form = TagForm(request.POST)
        if tag_form.is_valid():
            tag_form.save()
            return redirect(reverse('blog:manage_tag'))
        else:
            return render(request, 'blog-manage-tag.html',
                          {
                              'tag_form': tag_form,
                              'tags': tags,
                              'button_name': button_name,
                              'button_style': button_style,
                              'info': info
                          })
