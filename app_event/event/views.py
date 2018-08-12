from django.shortcuts import render
from .models import EventContent, EventProcess, Level, Project, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django.contrib.auth.models import User
from django.db.models import Count
from .forms import EventContentForm, FilterEventForm
from django.utils.decorators import method_decorator

# 分页模块添加 pip install django_pure_pagination
# 为不和Django自带的分页冲突，进行重命名
from pure_pagination import Paginator as pure_Paginator
from pure_pagination import EmptyPage as pure_EmptyPage
from pure_pagination import PageNotAnInteger as pure_PageNotAnInteger


def get_group_url_list(url):
    """
    将访问的url存储在列表中，用于前端判断
    EVENT_MENU_GROUP : 事件菜单组
    OTHER_MENU_GROUP : 其他菜单组
    :param url:
    :return:
    """
    group_url_list = list()
    group_url_list.append(url)
    return group_url_list


# 显示事件列表
def event(request, **kwargs):
    # print('视图**kwargs的值：', kwargs)
    if not kwargs:
        # 原来的事件列表和post筛选
        # events = EventContent.objects.all()
        queryset = EventContent.objects.all()
        if request.method == 'POST':
            visit_url = reverse('event:list')
            event_url_list = get_group_url_list(visit_url)

            filter_event_form = FilterEventForm(request.POST)
            if filter_event_form.is_valid():
                print('表单验证通过')
                user = filter_event_form.cleaned_data['user']
                status = filter_event_form.cleaned_data['status']
                project = filter_event_form.cleaned_data['project']
                category = filter_event_form.cleaned_data['category']
                level = filter_event_form.cleaned_data['level']
                queryset = queryset.filter(user=user, status=status, project=project, category=category, level=level)
                print(queryset)
        else:
            visit_url = reverse('event:list')
            event_url_list = get_group_url_list(visit_url)

            filter_event_form = FilterEventForm()

        """
        page = request.GET.get('page', 1)
        paginator = Paginator(queryset, settings.PAGE_NUM)  # paginator是分页对象
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)
        """
        # 使用pure_pagination
        try:
            page = request.GET.get('page', 1)
        except pure_PageNotAnInteger:
            page = 1
        # 这里指从events中取5个出来，每页显示5个，为了测试，可这儿只显示1个
        p = pure_Paginator(queryset, 10, request=request)
        events = p.page(page)

        return render(request, 'event.html',
                      {
                          'events': events,
                          'EVENT_MENU_GROUP': event_url_list,
                          'filter_event_form': filter_event_form,
                          'old_filter': True
                      })
    else:
        """
        多条件事件筛选
        event-(?P<user_id>\d+)-(?P<status_id>\d+)-(?P<level_id>\d+)-(?P<category_id>\d+)-(?P<project_id>\d+).html
        {'user_id': '0', 'status_id': '0', 'level_id': '0', 'category_id': '0', 'project_id': '0'}
        """
        filter_dict = dict()
        request_path = request.path
        # print('请求地址：', request_path)
        if kwargs['user_id'] != '0':
            filter_dict['user'] = get_object_or_404(User, id=kwargs['user_id'])
        if kwargs['status_id'] != '0':
            filter_dict['status'] = kwargs['status_id']
        if kwargs['level_id'] != '0':
            filter_dict['level'] = get_object_or_404(Level, id=kwargs['level_id'])
        if kwargs['category_id'] != '0':
            filter_dict['category'] = get_object_or_404(Category, id=kwargs['category_id'])
        if kwargs['project_id'] != '0':
            filter_dict['project'] = get_object_or_404(Project, id=kwargs['project_id'])

        user_list = User.objects.all().values('id', 'username')
        # print(user_list)
        # 将事件状态转换为字典列表形式
        status_list = list(map(lambda x: {'id': x[0], 'status_tag': x[1]}, EventContent.STATUS_CHOICES))
        # print(status_list)
        level_list = Level.objects.all().values('id', 'level_tag')
        category_list = Category.objects.all().values('id', 'category_name')
        project_list = Project.objects.all().values('id', 'project_name')

        url_id_list = kwargs.values()  # url中所有id：[0, 0, 0, 0, 0 ]
        visit_url = reverse('event:event_filter', args=url_id_list)

        event_url_list = get_group_url_list(visit_url)
        queryset = EventContent.objects.filter(**filter_dict)
        page = request.GET.get('page', 1)
        paginator = Paginator(queryset, settings.PAGE_NUM)  # paginator是分页对象
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)
        return render(request, 'event.html',
                      {
                          'events': events,
                          'EVENT_MENU_GROUP': event_url_list,
                          'visit_url': visit_url,  # 用于筛选事件active
                          'user_list': user_list,
                          'status_list': status_list,
                          'level_list': level_list,
                          'category_list': category_list,
                          'project_list': project_list,
                      })


# 事件处理过程
class ProcessView(View):
    """
    显示事件的处理过程
    """
    def get(self, request, event_pk):
        visit_url = reverse('event:process', args=[event_pk])
        event_url_list = get_group_url_list(visit_url)

        event = get_object_or_404(EventContent, pk=event_pk)
        # 事件处理的回复
        processes = EventProcess.objects.filter(event=event, choice='progress')
        # 事件处理的分析
        try:
            analysis = EventProcess.objects.filter(event=event, choice='analysis')[0]
        except IndexError:
            analysis = None
        # 先从用户筛选用户对该事件的处理，然后计算处理的次数
        users = User.objects.filter(event_process__event=event).annotate(reply_nums=Count('event_process'))
        return render(request, 'process.html',
                      {
                          'event': event,
                          'processes': processes,
                          'analysis': analysis,
                          'users': users,
                          'EVENT_MENU_GROUP': event_url_list
                      })


@login_required
def start_processing(request, event_pk):
    """
    事件开始处理，将事件的状态标记为2（处理中）
    :param request:
    :param event_pk: 事件id
    :return: 跳转到事件处理过程
    """
    event = get_object_or_404(EventContent, pk=event_pk)
    processes = EventProcess.objects.filter(event=event)
    username = request.user.username
    if request.method == 'POST':
        # print(event.status)
        reply = request.POST.get('reply', '')
        if event.status is None or event.status == 1:
            EventProcess.objects.create(
                choice='progress',
                reply='用户【{}】开始处理！'.format(username),
                event=event,
                user=request.user
            )
            # 更改处理状态
            event.status = 2
            event.save()
        # 如果有回复，直接修改
        if reply.split():
            EventProcess.objects.create(
                choice='progress',
                reply=reply,
                event=event,
                user=request.user
            )
    # return render(request, 'process.html', {'event': event, 'processes': processes})
    # 防止用户刷新页面导致POST重复提交
    # return HttpResponseRedirect('/event/{}'.format(event_pk))
    return redirect('event:process', event_pk=event_pk)


# 创建新事件
class CreateEvent(View):
    def get(self, request):
        """
        显示事件创建表单
        :param request:
        :return:
        """
        visit_url = reverse('event:event_create')
        event_url_list = get_group_url_list(visit_url)
        event_content_form = EventContentForm()
        return render(request, 'event_create.html',
                      {
                          'event_content_form': event_content_form,
                          'EVENT_MENU_GROUP': event_url_list
                      })

    @method_decorator(login_required(login_url='/account/login/?next=/event/create/'))
    def post(self, request):
        """
        提交事件表单，并且将事件状态修改为1（未处理）
        :param request:
        :return:
        """
        visit_url = reverse('event:event_create')
        event_url_list = get_group_url_list(visit_url)

        event_content_form = EventContentForm(request.POST, request.FILES)
        print(request.FILES)
        if event_content_form.is_valid():
            # 验证通过后，保存表单，然后添加user后提交表单保存到数据库
            event_content = event_content_form.save(commit=False)
            event_content.user = request.user
            # 创建事件，设置状态为未处理
            event_content.status = 1
            event_content.save()
            # reverse('event')的event代表视图的event，而不是url名称
            return redirect(reverse('event:list'))

        return render(request, 'event_create.html',
                      {
                          'event_content_form': event_content_form,
                          'EVENT_MENU_GROUP': event_url_list
                      })


# 事件处理完成
@login_required
def processed(request, event_pk):
    """
    事件处理完成，将事件状态修改为3（处理完成，待确认）
    :param request:
    :param event_pk:
    :return:
    """
    event = get_object_or_404(EventContent, pk=event_pk)
    event.status = 3
    event.save()
    EventProcess.objects.create(
        choice='progress',
        reply='用户【{}】处理完成，待确认完成！'.format(request.user.username),
        event=event,
        user=request.user
    )
    return redirect('event:process', event_pk=event_pk)


# 确认事件处理完成
@login_required
def confirm_processed(request, event_pk):
    """
    确认事件处理完成，将事件状态修改为5（确认完成）
    :param request:
    :param event_pk:
    :return:
    """
    event = get_object_or_404(EventContent, pk=event_pk)
    event.status = 5
    event.save()
    EventProcess.objects.create(
        choice='progress',
        reply='用户【{}】确认处理完成！'.format(request.user.username),
        event=event,
        user=request.user
    )
    return redirect('event:process', event_pk=event_pk)


# 事件关闭-状态变为6
@login_required
def event_close(request, event_pk):
    """
    事件完成关闭，将事件状态修改为6（关闭）
    :param request:
    :param event_pk:
    :return:
    """
    event = get_object_or_404(EventContent, pk=event_pk)
    event.status = 6
    event.save()
    EventProcess.objects.create(
        choice='progress',
        reply='用户【{}】关闭事件！'.format(request.user.username),
        event=event,
        user=request.user
    )
    return redirect('event:process', event_pk=event_pk)


# 提交事件分析post
@login_required
def submit_analysis(request, event_pk):
    """
    提交事件分析，如果事件处理完成在关闭之前，可以提交事件分析，修改状态为4（提交分析）
    :param request:
    :param event_pk:
    :return:
    """
    event = get_object_or_404(EventContent, pk=event_pk)
    analysis_reply = request.POST.get('analysis_reply', None)
    if analysis_reply and analysis_reply.split() != '':
        EventProcess.objects.create(
            choice='analysis',
            reply=analysis_reply,
            event=event,
            user=request.user
        )
        event.status = 4
        event.save()
    return redirect('event:process', event_pk=event_pk)


