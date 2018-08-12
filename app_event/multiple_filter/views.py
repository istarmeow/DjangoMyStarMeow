from django.shortcuts import render
from django.shortcuts import redirect, reverse
from event.views import get_group_url_list
from .models import Category, Code, Course

from .models import GoodsTag, FirstCategory, SubCategory, GoodsInfo
from django.shortcuts import get_object_or_404


def other1(request):
    visit_url = reverse('multiple_filter:other1')
    other_url_list = get_group_url_list(visit_url)
    return render(request, 'base_event.html', {'OTHER_MENU_GROUP': other_url_list})


def other2(request):
    visit_url = reverse('multiple_filter:other2')
    other_url_list = get_group_url_list(visit_url)
    return render(request, 'base_event.html', {'OTHER_MENU_GROUP': other_url_list})


def goods(request, **kwargs):
    if not kwargs:
        return redirect('multiple_filter:goods_filter', first_category_id='0', sub_category_id='0', tags_id='0', status_id='0')
    else:
        request_path = request.path
        print('\n当前请求路径：', request_path, '\n')
        print('kwargs：', kwargs)  # {'first_category_id': '0', 'sub_category_id': '0', 'tags_id': '0', 'status_id': '0'}

        goods_tag_list = GoodsTag.objects.all().values('id', 'name')
        first_category_list = FirstCategory.objects.all().values('id', 'name')
        sub_category_list = SubCategory.objects.all().values('id', 'name')
        status_list = list(map(lambda x: {'id': x[0], 'status': x[1]}, GoodsInfo.STATUS_CHOICES))
        filter_dict = dict()

        if kwargs['first_category_id'] == '0':
            # goods-0-x-x-x.html
            if kwargs['sub_category_id'] != '0':
                # goods-0-1-x-x.html
                sub_category = get_object_or_404(SubCategory, id=kwargs['sub_category_id'])
                # 选择二级分类后，由于多对一关系，一级分类也会跟着变化
                first_category_list = [{'id': sub_category.first_category.id, 'name': sub_category.first_category.name}]
                filter_dict['category'] = sub_category
        else:
            # 一级分类不为0，需要进行筛选
            # goods-1-x-x-x.html
            first_category = get_object_or_404(FirstCategory, id=kwargs['first_category_id'])
            sub_category_list = first_category.sub_categories.values('id', 'name')  # 选择一级分类后获取二级分类的列表
            if kwargs['sub_category_id'] != '0':
                sub_category = get_object_or_404(SubCategory, id=kwargs['sub_category_id'], first_category=first_category)
                # 选择二级分类后，由于多对一关系，一级分类也会跟着变化
                first_category_list = [{'id': sub_category.first_category.id, 'name': sub_category.first_category.name}]
                filter_dict['category'] = sub_category

        if kwargs['tags_id'] != '0':
            filter_dict['tags'] = kwargs['tags_id']

        if kwargs['status_id'] != '0':
            filter_dict['status'] = int(kwargs['status_id'])

        goods_list = GoodsInfo.objects.filter(**filter_dict)

        return render(request, 'goods.html',
                      {
                          'first_category_list': first_category_list,
                          'sub_category_list': sub_category_list,
                          'goods_tag_list': goods_tag_list,
                          'status_list': status_list,
                          'goods_list': goods_list
                      })


def course(request, *args, **kwargs):
    print(args, kwargs)  # () {'code_id': '0', 'category_id': '0', 'level_id': '0'}
    request_path = request.path  # http://127.0.0.1:8000/test/course-0-0-0.html

    # 筛选字典
    filter_dict = dict()

    code_list = Code.objects.all().values('id', 'name')
    category_list = Category.objects.all().values('id', 'name')
    level_list = list(map(lambda x: {'id': x[0], 'name': x[1]}, Course.LEVEL_CHOICE))

    if kwargs['code_id'] == '0':
        if kwargs['category_id'] != '0':
            category_list = Category.objects.filter(id=kwargs['category_id']).values('id', 'name')
            category = get_object_or_404(Category, id=kwargs['category_id'])
            # 分类不是全部，得到这个分类对应的所有编程语言
            code_list = category.codes.values('id', 'name')
            # 筛选这一分类
            filter_dict['category'] = category
    else:
        # 如果编程语言不为0，则获取对应的编程语言
        code = get_object_or_404(Code, id=kwargs['code_id'])
        # 得到编程语言对应的所有分类
        categories = code.category.all()
        category_list = categories.values('id', 'name')
        # 筛选课程在这些分类的结果
        filter_dict['category__in'] = categories
        if kwargs['category_id'] != '0':
            # 如果分类不为0，对分类进行筛选，得到该编程语言和该分类下的结果
            category = get_object_or_404(categories, id=kwargs['category_id'])
            code_list = category.codes.values('id', 'name')
            filter_dict['category'] = category

    if kwargs['level_id'] != '0':
        filter_dict['level'] = int(kwargs['level_id'])

    filter_dict['status'] = 1

    course_list = Course.objects.filter(**filter_dict)
    return render(request, 'course.html',
                  {
                      'category_list': category_list,
                      'code_list': code_list,
                      'level_list': level_list,
                      'course_list': course_list,
                  })


def course0(request, *args, **kwargs):
    # visit_url = reverse('test:course', args=args, kwargs=kwargs)
    # other_url_list = get_group_url_list(visit_url)

    # 访问http://127.0.0.1:8000/test/course-0-0-0.html，
    print(args, kwargs)  # 示例：() {'code_id': '0', 'category_id': '0', 'level_id': '0'}
    request_path = request.path
    print('\n当前请求路径：', request_path, '\n')
    # 从数据库获取课程信息时的filter条件字典
    filter_dict = dict()

    # 状态为上线的
    filter_dict['status'] = 1

    # 获取url中的课程分类id，或者使用kwargs.get('category_id')
    category_id = int(kwargs['category_id'])

    # 从数据库中获取所有的编程语言
    code_list = Code.objects.all().values('id', 'name')

    # print('所有编程语言code_list：', code_list)

    if kwargs['code_id'] == '0':
        """
        如果编程语言id是0，则显示所有编程语言
        """
        # 获取所有课程分类（包括所有课程分类的id和name）
        category_list = Category.objects.all().values('id', 'name')
        # 如果课程分类category_id也为0，即显示全部分类，什么都不用处理
        if kwargs['category_id'] == '0':
            pass
        else:
            # 如果课程分类不是全部，则过滤条件
            filter_dict['category_id__in'] = [category_id, ]
    else:
        """
        如果选择编程语言不为0，则进行筛选
        """
        if kwargs.get('category_id') == '0':
            # 分类category_id为0，选取所有分类
            # 获取已选择的编程语言
            code_obj = Code.objects.get(id=int(kwargs['code_id']))
            # 获取该编程语言下的所有视频分类
            category_list = code_obj.category.all().values('id', 'name')
            # 获取该编程语言下的所有的视频分类对应的分类id
            category_id_list = list(map(lambda x: x['id'], category_list))
            filter_dict['category_id__in'] = category_id_list
        else:
            code_obj = Code.objects.get(id=int(kwargs['code_id']))
            category_list = code_obj.category.all().values('id', 'name')
            category_id_list = list(map(lambda x: x['id'], category_list))
            filter_dict['category_id__in'] = [category_id, ]
            # 当前分类如果在获取的所有分类中，则方向下的所有相关分类显示
            # 当前分类如果不在获取的所有分类中，
            if int(kwargs['category_id']) in category_id_list:
                pass
            else:
                # 如果不在，获取指定编程语言的所有分类：选中的回到全部
                url_part_list = request_path.split('-')
                url_part_list[2] = '0'
                request_path = '-'.join(url_part_list)

    # 课程难度等级id
    level_id = int(kwargs['level_id'])
    if level_id == 0:
        pass
    else:
        # 过滤条件增加课程难度等级
        filter_dict['level'] = level_id

    # 取出筛选后的课程
    course_list = Course.objects.filter(**filter_dict).values('title', 'summary', 'image', 'video_url')
    # 把课程难度等级转化为单个标签是字典格式，整体是列表格式
    ret = map(lambda x: {'id': x[0], 'name': x[1]}, Course.LEVEL_CHOICE)
    level_list = list(ret)

    return render(request, 'course.html',
                  {
                      'category_list': category_list,
                      'code_list': code_list,
                      'level_list': level_list,
                      'current_url': request_path,
                      'course_list': course_list,
                      # 'OTHER_MENU_GROUP': other_url_list
                  })




