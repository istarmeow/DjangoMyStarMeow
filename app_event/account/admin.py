from django.contrib import admin
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = verbose_name = '用户'


class UserProfileAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_superuser', 'user_profile']
    inlines = (UserProfileInline, )


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)