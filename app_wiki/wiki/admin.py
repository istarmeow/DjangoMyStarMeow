from django.contrib import admin
from .models import Tag, ColorType
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from .models import TitleTree, WiKiContent, WiKiComment, WiKiContentImage, ThemeSetting, AuthorLog, CommentsLog


admin.site.register(Tag)


class ColorTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


admin.site.register(ColorType, ColorTypeAdmin)


# admin.site.register(TitleTree, MPTTModelAdmin)
admin.site.register(TitleTree, DraggableMPTTAdmin)  # 显示拖动


class WiKiContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'views', 'recommend', 'created_user', 'updated_user']


admin.site.register(WiKiContent, WiKiContentAdmin)


# WiKi回复
admin.site.register(WiKiComment, DraggableMPTTAdmin)


class WiKiContentImageAdmin(admin.ModelAdmin):
    list_display = ['wiki', 'title', 'image', 'created_user', 'created_time']


admin.site.register(WiKiContentImage, WiKiContentImageAdmin)


class ThemeSettingAdmin(admin.ModelAdmin):
    list_display = ['name', 'body_background', 'content_background', 'logo_color']


admin.site.register(ThemeSetting, ThemeSettingAdmin)


admin.site.register(AuthorLog)


admin.site.register(CommentsLog)