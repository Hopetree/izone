# -*- coding: utf-8 -*-
from oauth.models import Ouser
from rest_framework import serializers
from blog.models import Article, Tag, Category, Timeline
from tool.models import ToolLink, ToolCategory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ouser
        fields = ('id', 'username', 'first_name', 'link', 'avatar')
        # fields = '__all__'
        # exclude = ('password','email')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    keywords = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Article
        # fields = ('id', 'author', 'title', 'views', 'category', 'tags')
        # fields = '__all__'
        exclude = ('body',)


class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = '__all__'


class ToolCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolCategory
        fields = '__all__'


class ToolLinkSerializer(serializers.ModelSerializer):
    category = ToolCategorySerializer()

    class Meta:
        model = ToolLink
        fields = '__all__'
