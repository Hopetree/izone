# -*- coding: utf-8 -*-

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, IsAdminUser
from webstack.models import NavigationSite

from blog.models import Article, Tag, Category, Timeline
from oauth.models import Ouser
from tool.models import ToolLink
from .serializers import (UserSerializer, ArticleSerializer,
                          TimelineSerializer, TagSerializer,
                          CategorySerializer, ToolLinkSerializer,
                          NavigationSiteSerializer)


# from .permissions import IsAdminUserOrReadOnly

# RESEful API VIEWS
class UserListSet(viewsets.ModelViewSet):
    queryset = Ouser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class ArticleListSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    # 指定当前视图的认证方案，不使用全局认证方案
    authentication_classess = [BasicAuthentication, SessionAuthentication]
    # 指定当前视图的权限控制方案，不使用全局权限控制方案
    permission_classes = (IsAdminUser,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        # 仅返回 is_publish=True 的数据
        return Article.objects.filter(is_publish=True)


class TagListSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class CategoryListSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class TimelineListSet(viewsets.ModelViewSet):
    queryset = Timeline.objects.all()
    serializer_class = TimelineSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class ToolLinkListSet(viewsets.ModelViewSet):
    queryset = ToolLink.objects.all()
    serializer_class = ToolLinkSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class NavigationSiteListSet(viewsets.ModelViewSet):
    queryset = NavigationSite.objects.all()
    serializer_class = NavigationSiteSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        is_show = self.request.query_params.get('is_show', None)
        if is_show == 'true':
            queryset = queryset.filter(is_show=True)
        elif is_show == 'false':
            queryset = queryset.filter(is_show=False)
        return queryset
