from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# pip install django-mptt
from mptt.models import MPTTModel, TreeForeignKey


class ColorType(models.Model):
    name = models.CharField(max_length=50, verbose_name='颜色标记')
    code = models.CharField(max_length=50, default='default', verbose_name='颜色代码')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]
        verbose_name = '颜色对应'  # 后台显示模型名称
        verbose_name_plural = '颜色对应'


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


class TitleTree(MPTTModel):
    name = models.CharField(max_length=50, unique=True, verbose_name='标题')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='父标题')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    class MPTTMeta:
        order_insertion_by = ['created_time', 'name']  # 按照时间插入，新加的直接放在后面

    class Meta:
        verbose_name = 'WiKi标题'  # 后台显示模型名称
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def show_name(self):
        # 只显示6个字，超出部分使用省略号代替
        if len(str(self.name)) > 6:
            return "{}......".format(str(self.name)[:5])
        else:
            return str(self.name)


class WiKiContent(models.Model):
    STAR = (
        (1, '一星'),
        (2, '二星'),
        (3, '三星'),
        (4, '四星'),
        (5, '五星')
    )
    title = models.OneToOneField(TitleTree, on_delete=models.CASCADE, related_name='wiki_content', verbose_name='标题')
    content = models.TextField(verbose_name='正文')
    views = models.IntegerField(default=0, verbose_name='访问次数')
    tags = models.ManyToManyField(Tag, blank=True, related_name='wiki_content', verbose_name='标签')
    recommend = models.IntegerField(default=5, choices=STAR, verbose_name='推荐指数')
    author_message = models.CharField(max_length=100, blank=True, null=True, verbose_name='作者寄语')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='wiki_content', verbose_name='创建人')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    updated_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='修改人')

    class Meta:
        ordering = ['-updated_time']
        verbose_name = 'WiKi正文'
        verbose_name_plural = verbose_name

    def add_views(self):
        # 舍弃这种用法，使用Celery实现
        self.views += 1
        self.save(update_fields=['views'])

    def __str__(self):
        return self.title.name


class WiKiComment(MPTTModel):
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='wiki_comment', verbose_name='评论人')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    content = models.TextField(verbose_name='评论')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='评论')
    wiki = models.ForeignKey(WiKiContent, on_delete=models.CASCADE, related_name='wiki_comments', verbose_name='评论文章')

    def __str__(self):
        return self.content

    class MPTTMeta:
        order_insertion_by = ['-created_time']

    class Meta:
        verbose_name = 'WiKi评论'
        verbose_name_plural = verbose_name


# 图片存储
class WiKiContentImage(models.Model):
    wiki = models.ForeignKey(TitleTree, on_delete=models.CASCADE, null=True, blank=True, related_name='wiki_images', verbose_name='所属文章')
    title = models.CharField(max_length=50, null=True, blank=True, verbose_name='标题')
    image = models.ImageField(upload_to='images/wiki/%Y/%m', blank=True, null=True, verbose_name='图片')
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='wiki_images', verbose_name='上传人员')
    created_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间')

    class Meta:
        verbose_name = 'WiKi图集'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


# 前端主题设置
class ThemeSetting(models.Model):
    name = models.CharField(max_length=50, verbose_name='主题名称')
    body_background = models.ImageField(upload_to='theme/body', blank=True, null=True, verbose_name='页面背景')
    content_background = models.ImageField(upload_to='theme/content', blank=True, null=True, verbose_name='文本背景')
    logo_color = models.CharField(max_length=50, default='#E0BD62', verbose_name='Logo背景颜色')

    class Meta:
        verbose_name = '主题设置'
        verbose_name_plural = verbose_name
        ordering = ['name', ]

    def __str__(self):
        return self.name


# 作者动态日志
class AuthorLog(models.Model):
    OPERATE_CHOICES = (
        ('update', '更新了'),
        ('delete', '删除了'),
        ('create', '创建了'),
        ('move', '移动了')
    )
    operate = models.CharField(choices=OPERATE_CHOICES, max_length=20, blank=True, null=True, verbose_name='操作')
    title_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='文章标题')
    title_id = models.IntegerField(default=0, verbose_name='标题ID')
    message = models.CharField(max_length=200, blank=True, null=True, verbose_name='备注')
    created_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '作者动态'
        verbose_name_plural = verbose_name
        ordering = ['-created_time', ]

    def __str__(self):
        op_ch = dict(self.OPERATE_CHOICES)
        return "{}《{}》".format(op_ch[str(self.operate)], self.title_name)


# 用户评论日志
class CommentsLog(models.Model):
    OPERATE_CHOICES = (
        ('reply', '回复了'),
        ('delete', '删除了'),
        ('create', '评论了'),
    )
    user_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='用户名字')
    operate = models.CharField(choices=OPERATE_CHOICES, max_length=20, blank=True, null=True, verbose_name='操作')
    title_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='文章标题')
    title_id = models.IntegerField(default=0, verbose_name='标题ID')
    content = models.CharField(max_length=200, blank=True, null=True, verbose_name='内容')
    created_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '评论日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_time', ]

    def __str__(self):
        op_ch = dict(self.OPERATE_CHOICES)
        return "{}《{}》".format(op_ch[str(self.operate)], self.title_name)

