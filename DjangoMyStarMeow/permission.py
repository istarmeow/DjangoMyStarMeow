from django.shortcuts import render
# 自定义权限，超级用户权限，以及需要登录权限
from functools import wraps
from django.urls import reverse_lazy  # next_url=reverse_lazy('account:login')
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound


def permission_forbidden(http_exception=403, next_url=reverse_lazy('account:login')):
    """
    Usage:
    @permission_forbidden(403)
    def test(request):
        return HttpResposne('hello world')

    when decorated by permission_forbidden,if the user is not staff,
    it will raise one PerissionDenied exception

    use in url
    from .views import permission_forbidden

    url(r'wiki_backend/$', permission_forbidden(http_exception=403)(wiki_content_backend), name='wiki_content_backend'),
    url(r'^edit/title_id/$', permission_forbidden(http_exception=403)(WiKiContentEdit.as_view()), name='wiki_edit'),

    :param http_exception:
    :return:the return value of decorated function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, **kwargs):
            if http_exception == 403:
                # （禁止） 服务器拒绝请求。
                if request.user.is_superuser:
                    # user.is_staff：决定用户是否可以访问admin管理界面。默认False。
                    # user.is_superuser：默认False。当设为True时，用户获得全部权限。
                    rv = func(request, **kwargs)
                    return rv
                else:
                    # raise PermissionDenied  # 网页返回“403 Forbidden”
                    return render(request, 'backend_error.html',
                                  {
                                      'error_code': http_exception,
                                      'msg': '非管理员无法访问'
                                  })  # 将返回一个地址
            elif http_exception == 401:
                # （未授权） 请求要求身份验证。 对于需要登录的网页，服务器可能返回此响应。
                if not request.user.is_authenticated():
                    return HttpResponseRedirect(next_url)
            rv = func(request, **kwargs)
            return rv

        return wrapper

    return decorator

