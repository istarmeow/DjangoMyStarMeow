from django.contrib import admin
from .models import *


admin.site.register(Project)

admin.site.register(Category)

admin.site.register(Level)


class EventContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'project', 'category', 'level', 'start_time', 'end_time', 'pause_time']


admin.site.register(EventContent, EventContentAdmin)


class EventProcessAdmin(admin.ModelAdmin):
    list_display = ['event', 'choice', 'reply', 'created', 'updated']


admin.site.register(EventProcess, EventProcessAdmin)
