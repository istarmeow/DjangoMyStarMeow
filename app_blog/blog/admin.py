from django.contrib import admin
from .models import Tag, Category, Article, BlogImage, BlogNotice


admin.site.register(Tag)


admin.site.register(Category)


admin.site.register(Article)


class BlogImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'image', 'extension', 'size']
    list_filter = ['extension']


admin.site.register(BlogImage, BlogImageAdmin)


admin.site.register(BlogNotice)

