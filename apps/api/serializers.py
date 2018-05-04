# -*- coding: utf-8 -*-
from oauth.models import Ouser
from rest_framework import serializers
from blog.models import Article, Tag, Category, Timeline


class UserSerializer(serializers.ModelSerializer):
    article_set = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title'
    )

    class Meta:
        model = Ouser
        fields = ('id', 'username', 'first_name', 'link', 'avatar', 'article_set')
        # fields = '__all__'
        # exclude = ('password','email')


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    category = serializers.ReadOnlyField(source='category.name')
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
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

class TagSerializer(serializers.ModelSerializer):
    article_set = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title'
    )
    class Meta:
        model = Tag
        # fields = ('id', 'name', 'slug')
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    article_set = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title'
    )
    class Meta:
        model = Category
        # fields = ('id', 'name', 'slug')
        fields = '__all__'


class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        # fields = ('id', 'title', 'star_num', 'update_date')
        fields = '__all__'
