from django.db import models
from django.utils.timezone import now


class GoodsTag(models.Model):
    name = models.CharField(max_length=64, verbose_name='标签名称')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]
        verbose_name = '商品标签'  # 后台显示模型名称
        verbose_name_plural = verbose_name


# 智能家居、手机、电视、电脑
class FirstCategory(models.Model):
    name = models.CharField(max_length=64, verbose_name='分类名称')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]
        verbose_name = '一级分类'
        verbose_name_plural = verbose_name


# 小米6、小米8、红米10
class SubCategory(models.Model):
    name = models.CharField(max_length=64, verbose_name='分类名称')
    first_category = models.ForeignKey(FirstCategory, related_name='sub_categories', verbose_name='上级分类')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]
        verbose_name = '二级分类'
        verbose_name_plural = verbose_name


class GoodsInfo(models.Model):
    STATUS_CHOICES = (
        (1, '上架'),
        (2, '下架'),
    )

    title = models.CharField(max_length=100, verbose_name='标题')
    content = models.TextField(blank=True, null=True, verbose_name='正文')
    image = models.FileField(upload_to='images/goods/%Y/%m', blank=True, null=True, verbose_name='图片')
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name='状态')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    publish_time = models.DateTimeField(blank=True, null=True, default=now, verbose_name='发布时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='goods_info', verbose_name='所属分类')
    tags = models.ManyToManyField(GoodsTag, blank=True, verbose_name='标签集合')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '商品信息'
        verbose_name_plural = verbose_name


# 课程分类
class Category(models.Model):
    weight = models.IntegerField(verbose_name='权重（按从大到小排列）', default=0)
    name = models.CharField(max_length=32, verbose_name='分类名称')

    class Meta:
        verbose_name = '分类方向'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 编程语言，一个课程分类里可能有多种编程语言，一种编程语言可能存在不同的课程分类
class Code(models.Model):
    weight = models.IntegerField(default=0, verbose_name='权重（按从大到小排列）')
    name = models.CharField(max_length=32, verbose_name='编程语言')
    category = models.ManyToManyField(Category, related_name='codes', verbose_name='课程分类')

    class Meta:
        verbose_name = '编程语言'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 课程详情
class Course(models.Model):
    STATUS_CHOICE = (
        (0, '下线'),
        (1, '上线')
    )

    LEVEL_CHOICE = (
        (1, '初级'),
        (2, '中级'),
        (3, '高级')
    )

    status = models.IntegerField(choices=STATUS_CHOICE, default=1, verbose_name='状态')
    level = models.IntegerField(choices=LEVEL_CHOICE, default=1, verbose_name='难度级别')
    category = models.ForeignKey(Category, null=True, blank=True, related_name='courses', verbose_name='课程分类')
    weight = models.IntegerField(default=0, verbose_name='权重（按从大到小排列）')
    title = models.CharField(max_length=32, verbose_name='标题')
    summary = models.CharField(max_length=100, verbose_name='简介')
    image = models.ImageField(upload_to='images/course/%Y/%m', verbose_name='图片')
    video_url = models.CharField(max_length=256, verbose_name='视频地址')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '课程详情'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
