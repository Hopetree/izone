# -*- coding: utf-8 -*-
from oauth.models import Ouser
from rest_framework import serializers
from .models import Article, Tag, Category, Timeline


class UserSerializer(serializers.ModelSerializer):
    article_set = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title'
    )
    class Meta:
        model = Ouser
        fields = ('id', 'username', 'article_set')


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    category = serializers.ReadOnlyField(source='category.name')
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Article
        fields = ('id', 'author', 'title', 'views', 'category', 'tags')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id','name','slug')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id','name','slug')

class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = ('id','title','star_num','update_date')
