# -*- coding: utf-8 -*-


from oauth.models import Ouser
from blog.models import Article, Tag, Category, Timeline
from .serializers import (UserSerializer, ArticleSerializer,
                          TimelineSerializer,TagSerializer,CategorySerializer)
from rest_framework import viewsets, permissions

# RESEful API VIEWS
class UserListSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ouser.objects.all()
    serializer_class = UserSerializer

class ArticleListSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

class TagListSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class CategoryListSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TimelineListSet(viewsets.ReadOnlyModelViewSet):
    queryset = Timeline.objects.all()
    serializer_class = TimelineSerializer