from django.contrib import admin
from .models import *


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['weight', 'name']


admin.site.register(Category, CategoryAdmin)


class CodeAdmin(admin.ModelAdmin):
    list_display = ['weight', 'name']


admin.site.register(Code, CodeAdmin)


class CourseAdmin(admin.ModelAdmin):
    list_display = ['status', 'level', 'category', 'weight', 'title']


admin.site.register(Course, CourseAdmin)


class GoodsTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


admin.site.register(GoodsTag, GoodsTagAdmin)


class FirstCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'first_category']


class GoodsInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'category']


admin.site.register(FirstCategory, FirstCategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(GoodsInfo, GoodsInfoAdmin)