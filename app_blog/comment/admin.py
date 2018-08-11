from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import BlogComment


# admin.site.register(BlogComment)


class BlogCommentAdmin(MPTTModelAdmin):
    list_filter = ['blog', ]


admin.site.register(BlogComment, BlogCommentAdmin)