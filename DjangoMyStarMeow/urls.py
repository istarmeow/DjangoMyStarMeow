"""DjangoMyStarMeow URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from account.views import index

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^event/', include('event.urls', namespace='event')),  # 事件系统
    url(r'^multiple_filter/', include('multiple_filter.urls', namespace='multiple_filter')),  # 多条件筛选测试
    url(r'^account/', include('account.urls', namespace='account')),  # 用户认证
    url(r'^wiki/', include('wiki.urls', namespace='wiki')),  # WiKi应用
    url(r'^$', index, name='index'),
    url(r'^index.html$', index, name='index'),
    url(r'hitcount/', include('hitcount.urls', namespace='hitcount')),  # 点击数
    url(r'^blog/', include('blog.urls', namespace='blog')),  # Blog应用
    url(r'^comment/', include('comment.urls', namespace='comment')),  # 评论应用
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)