from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from markdown import markdown
from django.utils.html import mark_safe


class Tag(models.Model):
    name = models.CharField(max_length=64, verbose_name='标签名称')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]
        verbose_name = '标签名称'  # 后台显示模型名称
        verbose_name_plural = '标签列表'


class Category(models.Model):
    name = models.CharField(max_length=64, verbose_name='分类名称')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]
        verbose_name = '分类名称'
        verbose_name_plural = '分类列表'


# 已发布的-模型管理器
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published').order_by("-publish_time")


# 草稿-模型管理器
class DraftManager(models.Manager):
    def get_queryset(self):
        return super(DraftManager, self).get_queryset().filter(status='draft')


class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '发布'),
    )
    title = models.CharField(max_length=100, verbose_name='标题')
    author = models.ForeignKey(User, related_name='blog_posts', verbose_name='作者')
    content = models.TextField(blank=True, null=True, verbose_name='正文')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published', verbose_name='状态')
    views = models.PositiveIntegerField(default=0, verbose_name='浏览量')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    publish_time = models.DateTimeField(blank=True, null=True, default=now, verbose_name='发布时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=False, null=False, related_name='articles', verbose_name='所属分类')
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles', verbose_name='标签集合')

    objects = models.Manager()  # 默认的模型管理器
    published = PublishedManager()  # 自定义模型管理器，只显示已发布的
    draft = DraftManager()  # 自定义模型管理器，只显示草稿

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-publish_time', ]  # 按照发布时间降序，旧的时间在后，也就是新发布的博客放在前面
        verbose_name = '文章'
        verbose_name_plural = '文章列表'

    def viewed(self):
        """
        更新浏览量
        """
        self.views += 1
        self.save(update_fields=['views'])

    def get_content_as_markdown(self):
        # 不太好用
        return mark_safe(markdown(self.content, safe_mode='escape'))

    # 显示前一篇博客
    def prev_article(self):
        # 显示前一篇，前一篇的id比当前id小，状态为已发布，发布时间不为空
        return Article.published.filter(id__lt=self.id, publish_time__isnull=False).first()

    # 显示后一篇博客
    def next_article(self):
        # 显示下一篇，下一篇的id比当前id大，状态为已发布，发布时间不为空
        return Article.published.filter(id__gt=self.id, publish_time__isnull=False).last()


# 图片存储
class BlogImage(models.Model):
    title = models.CharField(max_length=50, null=True, blank=True, verbose_name='标题')
    image = models.ImageField(upload_to='images/blog/%Y/%m', blank=True, null=True, verbose_name='图片')
    extension = models.CharField(max_length=20, blank=True, null=True, verbose_name='扩展名')
    size = models.FloatField(blank=True, null=True, verbose_name='图片大小(KB)')
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='blog_images', verbose_name='上传人员')
    created_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '博客图集'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


# 博客公告
class BlogNotice(models.Model):
    slug = models.SlugField(max_length=10, default='new', editable=False, verbose_name='短链')  # 默认一个不可编辑
    blogger = models.CharField(max_length=10, default='@LR', verbose_name='博主')
    title = models.CharField(max_length=20, default='个人博客', verbose_name='公告标题')
    content = models.TextField(blank=True, null=True, default="这是我的个人博客，欢迎", max_length=1000, verbose_name='公告')

    class Meta:
        verbose_name = '博客公告'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content
