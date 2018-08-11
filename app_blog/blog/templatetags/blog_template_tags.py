from django import template
from blog.models import Tag, Category, Article
from comment.models import BlogComment
from django.core.urlresolvers import reverse
import random

register = template.Library()


# 返回博客列表URL
@register.simple_tag
def get_list_url(user):
    if user.is_superuser:
        return reverse('blog:blog_list')
    else:
        return reverse('blog:blog_list_public')


# 返回博客分类的URL
@register.simple_tag
def get_category_url(user, category_id):
    kw = {"category_id": category_id}
    if user.is_superuser:
        return reverse('blog:blog_list_with_category', kwargs=kw)
    else:
        return reverse('blog:blog_list_with_category_public', kwargs=kw)


# 返回博客详情URL
@register.simple_tag
def get_detail_url(user, blog_id):
    kw = {"article_id": blog_id}
    if user.is_superuser:
        return reverse('blog:blog_detail', kwargs=kw)
    else:
        return reverse('blog:blog_detail_public', kwargs=kw)


# 返回个分类已发布博客数量
@register.simple_tag
def get_published_nums(catogory):
    return Article.published.filter(category=catogory).count()


# 获取该日期的博客数量，按照日期归档
@register.simple_tag
def year_month_blog_nums(year, month):
    return Article.published.filter(publish_time__year=year, publish_time__month=month).count()


# 根据用户类型返回年月归档链接
@register.simple_tag
def get_year_month_url(user, year, month):
    kw = {"year": year, 'month': month}
    if user.is_superuser:
        return reverse('blog:blog_list_year_month', kwargs=kw)
    else:
        return reverse('blog:blog_list_year_month_public', kwargs=kw)


# 取随机颜色
@register.simple_tag
def random_color_flag():
    color_flag_list = ['default', 'primary', 'info', 'success', 'warning', 'danger', 'white']
    return random.choice(color_flag_list)


# 根据用户类型返回标签归档链接
@register.simple_tag
def get_tag_url(user, tag_id):
    kw = {"tag_id": tag_id}
    if user.is_superuser:
        return reverse('blog:blog_list_tag', kwargs=kw)
    else:
        return reverse('blog:blog_list_tag_public', kwargs=kw)


# 根据用户类型返回搜索结果
@register.simple_tag
def get_search_url(user):
    kw = {}
    if user.is_superuser:
        return reverse('blog:blog_list_search', kwargs=kw)
    else:
        return reverse('blog:blog_list_search_public', kwargs=kw)


# 把非根节点显示在一起，用相同的样式，插入到根节点中
def get_comment_children(request, comment_children, blog, csrf_token, flag=1):
    # print(blog, type(blog))
    html = ""
    for comment in comment_children.get_children():
        html += '''
        <div class="social-comment">
            {indent1}  <!-- 缩进标识 -->
            
                <a class="pull-left">
                    <img alt="image" src="{image_url}">
                </a>
                <div class="media-body">                
                    <div class="row">
                        <div class="col-md-8">
                            <a>{username}</a>
                            回复
                            <a>{username_parent}</a>：
                            {content}
                            </div>
                        <div class="col-md-4 text-right" title="登录后才能评论">
                            {i_reply}  <!-- 显示回复按钮，如果是自己回复的，则不显示回复按钮 -->
                        </div>
                    </div>
    
                    <a class="small"><i class="fa fa-thumbs-up"></i> 0</a> -
                    <small class="text-muted">{created_time}</small>
    
                    <!-- 显示或隐藏回复表单 -->
                    <div style="display: none" id="id_show_reply_{parent_comment_id}">
                        <form id="jsStayForm{parent_comment_id}">
                            <div class="col-md-8 col-md-offset-4 input-group text-right">                                        
                                <input name="parent_comment_id" value="{parent_comment_id}" hidden>
                                <input name="blog_id" value="{blog_id}" hidden>
                                <input name="content" type="text" class="form-control" placeholder="回复 {username}："> 
                                <span class="input-group-btn"> 
                                    <button type="button" class="btn btn-default" id="jsStayBtn{parent_comment_id}">回复</button> 
                                </span>
                            </div>
                        </form>
                    </div>
                    
                    <script>
                        function showReplyFrom{parent_comment_id}() {{
                            let div_element = document.getElementById("id_show_reply_{parent_comment_id}");
                            if (div_element.style.display === "none") {{
                                {click_operate};
                            }}	else {{
                                div_element.style.display="none";
                            }}
                        }}
                        
                        
                        $(function(){{
                            $('#jsStayBtn{parent_comment_id}').on('click', function(){{                
                                $.ajax({{
                                    cache: false,
                                    type: "POST",
                                    url:"{create_comment_url}",
                                    data:$('#jsStayForm{parent_comment_id}').serialize(),
                                    dateType:"json",
                                    async: true,
                                    beforeSend:function(xhr, settings){{
                                        xhr.setRequestHeader("X-CSRFToken", "{csrf_token}");
                                    }},
                                    success: function(data) {{
                                        if(data.status === 'success'){{
                                            alert("提交成功");
                                            window.location.reload();  //刷新当前页面.
                                        }} else if(data.status === 'fail'){{
                                            alert("提交发生错误，内容不能为空");
                                        }}
                                    }},
                                }});
                            }});
                        }})
                                   
                    </script>
                    
                {indent2}  <!-- 缩进标识 -->
            </div>
        </div>{hr}
        '''.format(
            image_url=comment.created_user.user_profile.image.url,  # 创建评论的人头像
            username=comment.created_user.username,  # 创建这条回复的人名字
            username_parent=comment.parent.created_user.username,  # 这条回复是回复谁的名字
            created_time=comment.created_time.strftime("%Y-%m-%d %H:%M:%S"),  # 创建这条回复的时间
            content=comment.content,  # 这条回复的内容
            parent_comment_id=comment.id,  # 评论的ID，用于提交评论时的父ID
            blog_id=blog.id,  # 回复的博客ID
            csrf_token=csrf_token,   # 从前端把token传进来，否则js提交禁止
            create_comment_url=reverse('comment:blog_comment_create'),
            i_reply='<i class="fa fa-commenting-o" onclick="showReplyFrom' + str(comment.id) + '()"></i>' if request.user != comment.created_user else "",  # 自己回复的将不显示回复按钮
            click_operate='div_element.style.display="block";' if request.user.is_authenticated() else 'alert("需要登录才能回复")',  # 如果是未登录，点击回复按钮提示登录
            hr="<hr style='margin-top:5px;margin-bottom:0px; border-top: 5px solid #eee;' />" if flag == 1 else "",  # 如果是回复评论，则flag=1，则显示一条很闲
            indent1='<div class="social-comment">' if flag == 0 else '',  # 当为子节点第一个时flag=1，如果该节点还有自己点，则将flag变为0，进行缩进
            indent2='</div>' if flag == 0 else '',
        )
        # print(comment, type(comment))
        # 递归获取该节点的子节点值，并和前面的结果相加
        if comment.get_children():
            html += get_comment_children(request, comment, blog, csrf_token, flag=0)
    return html


# 层级显示用户对博客的评论
@register.simple_tag
def comment_list_view(request, flag, blog, csrf_token, comments):
    # print(blog, comments)
    # print(request)
    # flag：访问标识，blog：博客实例->blog_article，comments：博客评论->blog_article.comment_all
    all_comments = comments
    if int(flag) == 1:
        all_comments = BlogComment.objects.filter(blog=blog)
    html = ""
    for comment in all_comments:
        # 显示所有根节点，设置为一个样式
        if comment.is_root_node():
            html += '''
            <br>
            <div class="social-feed-box">
                <div class="social-avatar">
                    <a class="pull-left">
                        <img alt="image" src="{image_url}">
                    </a>
                    <div class="media-body">
                        <a>{username}</a>
                        <small class="text-muted">{created_time}</small>
                    </div>
                </div>
                <div class="social-body">
                     <div class="row">
                        <div class="col-md-8">
                            <p>{content}</p>
                        </div>
                        <div class="col-md-4 text-right" title="登录后才能评论">
                            {i_reply}
                        </div>
                    </div>
                    
                    <!-- 显示或隐藏回复表单 -->
                    <div style="display: none" id="id_show_reply_{parent_comment_id}">
                        <form id="jsStayForm{parent_comment_id}">
                            <div class="col-md-9 col-md-offset-3 input-group text-right">                                        
                                <input name="parent_comment_id" value="{parent_comment_id}" hidden>  <!--因为是对评论的回复，所以需要该评论的id作为回复的父节点-->
                                <input name="blog_id" value="{blog_id}" hidden>
                                <input name="content" type="text" class="form-control" placeholder="回复 {username}："> 
                                <span class="input-group-btn"> 
                                    <button type="button" class="btn btn-primary" id="jsStayBtn{parent_comment_id}">回复</button> 
                                </span>
                            </div>
                        </form>
                    </div>
                    
                <script>
                    function showReplyFrom{parent_comment_id}() {{
                        let div_element = document.getElementById("id_show_reply_{parent_comment_id}");
                        if (div_element.style.display === "none") {{
                            {click_operate};
                        }}	else {{
                            div_element.style.display="none";
                        }}
                    }}
                    
                    
                    $(function(){{
                        $('#jsStayBtn{parent_comment_id}').on('click', function(){{                
                            $.ajax({{
                                cache: false,
                                type: "POST",
                                url:"{create_comment_url}",
                                data:$('#jsStayForm{parent_comment_id}').serialize(),
                                dateType:"json",
                                async: true,
                                beforeSend:function(xhr, settings){{
                                    xhr.setRequestHeader("X-CSRFToken", "{csrf_token}");
                                }},
                                success: function(data) {{
                                    if(data.status === 'success'){{
                                        alert("提交成功");
                                        window.location.reload();  //刷新当前页面.
                                    }} else if(data.status === 'fail'){{
                                        alert("提交发生错误");
                                    }}
                                }},
                            }});
                        }});
                    }})
                               
                </script>           
                    
                </div>
                <div class="social-footer">
                    {comment_children}                                       
                </div>   
            </div>                                                            
            '''.format(
                image_url=comment.created_user.user_profile.image.url,
                username=comment.created_user.username,
                created_time=comment.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                content=comment.content,
                parent_comment_id=comment.id,
                blog_id=blog.id,
                csrf_token=csrf_token,
                create_comment_url=reverse('comment:blog_comment_create'),
                i_reply='<i class="fa fa-commenting" title="交流一下想法吧~" onclick="showReplyFrom' + str(comment.id) + '()"></i>' if request.user != comment.created_user else "",  # 自己回复的将不显示回复按钮
                click_operate='div_element.style.display="block";' if request.user.is_authenticated() else 'alert("需要登录才能回复")',  # 如果是未登录，点击回复按钮提示登录
                comment_children=get_comment_children(request, comment, blog, csrf_token)
            )
    return html

