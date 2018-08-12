from django import forms
from .models import EventContent


class EventContentForm(forms.ModelForm):
    class Meta:
        model = EventContent
        fields = ('title', 'content', 'image', 'project', 'category', 'level', 'end_time')


class FilterEventForm(forms.ModelForm):
    class Meta:
        model = EventContent
        fields = ('user', 'status', 'project', 'category', 'level')