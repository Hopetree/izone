from django.shortcuts import render,redirect

from blog.models import Article
from .models import ArticleComment
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

user_model = settings.AUTH_USER_MODEL

@login_required
@require_POST
def AddcommentView(request):
    if request.is_ajax():
        data = request.POST
        new_user = request.user
        new_content = data.get('content')
        article_id = data.get('article_id')
        rep_id = data.get('rep_id')
        the_article = Article.objects.get(id=article_id)
        if not rep_id:
            new_comment = ArticleComment(author=new_user,content=new_content,belong=the_article,parent=None,rep_to=None)
        else:
            new_rep_to = ArticleComment.objects.get(id=rep_id)
            new_parent = new_rep_to.parent if new_rep_to.parent else new_rep_to
            new_comment = ArticleComment(author=new_user, content=new_content, belong=the_article, parent=new_parent, rep_to=new_rep_to)
        new_comment.save()
        new_point = '#com-' + str(new_comment.id)
        return JsonResponse({'msg':'评论提交成功！','new_point':new_point})
    return JsonResponse({'msg': '评论失败！'})



