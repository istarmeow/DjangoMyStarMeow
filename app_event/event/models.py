from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# pip install markdown
from markdown import markdown
from django.utils.html import mark_safe


# 项目分类
class Project(models.Model):
    project_name = models.CharField(max_length=10, verbose_name='项目名称')

    class Meta:
        ordering = ['project_name']
        verbose_name = '项目分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.project_name


# 事件分类
class Category(models.Model):
    category_name = models.CharField(max_length=10, verbose_name='分类名称')

    class Meta:
        ordering = ['category_name', ]
        verbose_name = '事件分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category_name


# 事件级别
class Level(models.Model):
    order_number = models.PositiveIntegerField(unique=True, verbose_name='级别编号')
    level_tag = models.CharField(max_length=10, verbose_name='级别名称')

    class Meta:
        ordering = ['order_number', ]
        verbose_name = '事件级别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.level_tag


# 事件内容
class EventContent(models.Model):
    STATUS_CHOICES = (
        (1, '未处理'),
        (2, '处理中'),
        (3, '完成'),
        (4, '提交分析'),
        (5, '确认完成'),
        (6, '已关闭')
    )
    title = models.CharField(max_length=50, verbose_name='事件标题')
    content = models.TextField(verbose_name='事件正文')
    image = models.ImageField(upload_to='images/event/%Y/%m', blank=True, null=True, verbose_name='描述图片')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name='事件状态')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='event_content', verbose_name='项目分类')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='event_content', verbose_name='事件分类')
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True, related_name='event_content', verbose_name='事件级别')
    user = models.ForeignKey(User, related_name='event_content', on_delete=models.CASCADE, verbose_name='创建人')
    start_time = models.DateTimeField(default=timezone.now, verbose_name='事件开始时间')
    end_time = models.DateTimeField(default=timezone.now, verbose_name='事件结束时间')
    pause_time = models.DateTimeField(default=timezone.now, verbose_name='事件暂停时间')

    class Meta:
        ordering = ['-created']
        verbose_name = '事件内容'
        verbose_name_plural = verbose_name

    def time_interval(self):
        time_diff = self.end_time - timezone.now()
        days = time_diff.days
        seconds = time_diff.seconds
        minutes = seconds // 60  # 得到这些秒换算的分钟整数
        second = seconds % 60  # 得到除去分钟后剩余的秒数
        hours = minutes // 60
        minute = minutes % 60
        if self.status == 6:
            return '事件已关闭！'
        if days <= -1:
            return '处理已超时！'

        return '{}天{}时{}分'.format(days, hours, minute)

    def __str__(self):
        return self.title

    def get_content_as_markdown(self):
        """
        当使用Mardown功能时，我们需要先让它转义一下特殊字符，然后再解析出Markdown标签。
        这样做之后，输出字符串可以安全的在模板中使用。
        :return:
        """
        return mark_safe(markdown(self.content, safe_mode='escape'))


# 事件处理
class EventProcess(models.Model):
    PROCESS_CHOICE = (
        ('progress', '过程进度'),
        ('analysis', '事件分析')
    )
    choice = models.CharField(choices=PROCESS_CHOICE, max_length=20, default='progress', verbose_name='事件过程分析')
    reply = models.TextField(verbose_name='事件回复')
    event = models.ForeignKey(EventContent, on_delete=models.CASCADE, related_name='event_process', verbose_name='事件内容')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    user = models.ForeignKey(User, related_name='event_process', verbose_name='创建人')

    class Meta:
        ordering = ['created']
        verbose_name = '事件处理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.reply[:20]

    def get_reply_as_markdown(self):
        """
        当使用Mardown功能时，我们需要先让它转义一下特殊字符，然后再解析出Markdown标签。
        这样做之后，输出字符串可以安全的在模板中使用。
        :return:
        """
        return mark_safe(markdown(self.reply, safe_mode='escape'))
        # return markdown(self.reply)