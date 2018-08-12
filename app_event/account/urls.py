from django.conf.urls import url
from . import views
# 重写的默认模板路径为：..\Python36\Lib\site-packages\django\contrib\admin\templates\registration ，必须是registration目录下。
# 在account应用中的templates目录下创建一个新的目录命名为registration。这个路径是Django认证视图期望认证模板默认的存放路径
from django.contrib.auth.views import login, logout, logout_then_login
from django.contrib.auth.views import password_change, password_change_done
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete

from .views import verify_image, my_login


urlpatterns = [
    # url(r'^login/$', login, name='login'),
    url(r'^login/$', my_login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^verify_image/(\d+)/(\d+)/$', verify_image, name='verify_image')  # http://127.0.0.1:8000/account/verify_image/200/80/
]