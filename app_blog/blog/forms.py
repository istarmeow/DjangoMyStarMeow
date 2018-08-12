from django import forms
from .models import Article, BlogNotice, Category, Tag


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        # fields = '__all__'  # 选择所有字段，或者通过列表方式选择需要的字段
        exclude = ['author', 'views']  # 排除字段

    def clean_title(self):
        title = self.cleaned_data['title']
        if title.strip() == '':
            raise forms.ValidationError('标题不能为空')
        return title

    def clean_content(self):
        content = self.cleaned_data['content']
        if content.strip() == '':
            raise forms.ValidationError('内容不能为空')
        return content


class BlogNoticeForm(forms.ModelForm):
    class Meta:
        model = BlogNotice
        exclude = ['slug']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"

    def clean_name(self):
        name = self.cleaned_data['name']
        if Category.objects.filter(name=name.strip()):
            # print('已存在的名称')
            raise forms.ValidationError('分类名称已存在')
        return name


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"

    def clean_name(self):
        name = self.cleaned_data['name']
        if Tag.objects.filter(name=name.strip()):
            # print('已存在的名称')
            raise forms.ValidationError('分类名称已存在')
        return name
