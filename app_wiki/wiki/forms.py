from django import forms
from .models import WiKiContentImage, WiKiComment, ThemeSetting
import re


class WiKiCommentForm(forms.ModelForm):
    class Meta:
        model = WiKiComment
        fields = ['content']


class ThemeSettingForm(forms.ModelForm):
    class Meta:
        model = ThemeSetting
        fields = "__all__"

    def clean_logo_color(self):
        """
        验证颜色代码是否符合规范
        """
        logo_color = self.cleaned_data['logo_color']
        color_code_regex = r'^#[a-zA-Z0-9]{3,6}$'
        cp = re.compile(color_code_regex)
        if cp.match(logo_color):
            return logo_color
        else:
            raise forms.ValidationError('请输入以#开头的3-6位颜色代码', code='invalid logo_color')

    @staticmethod
    def valid_image(image_name):
        """
        验证图片后缀
        """
        image_regex = r'.*(.jpg|.png|.gif)$'
        cp = re.compile(image_regex)
        if not cp.match(image_name.lower()):
            print('图片验证不通过')
            return False
        return True

    def clean_body_background(self):
        body_background = self.cleaned_data['body_background']
        print(body_background)
        if not body_background or self.valid_image(body_background.name) is False:
            raise forms.ValidationError('请选择jpg、png或gif格式的图片')
        return body_background

    def clean_content_background(self):
        content_background = self.cleaned_data['content_background']
        if not content_background or self.valid_image(content_background.name) is False:
            raise forms.ValidationError('请选择jpg、png或gif格式的图片')
        return content_background


class WiKiContentImageForm(forms.ModelForm):
    class Meta:
        model = WiKiContentImage
        fields = '__all__'
