from django.db import models
from django.contrib.auth.models import User
from wiki.models import ThemeSetting


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile', verbose_name='用户')
    image = models.ImageField(upload_to='account/%Y/%m', default='account/default.jpg', blank=True, null=True, verbose_name='头像')
    theme = models.ForeignKey(ThemeSetting, null=True, blank=True, on_delete=models.SET_NULL, related_name='user_profile', verbose_name='主题')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username
