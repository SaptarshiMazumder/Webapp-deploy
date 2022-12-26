from rest_framework import serializers

from .models import Post, Category, ImageFiles


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        # fields = '__all__'
        # fields = ('title', 'body', 'category')
        fields = ('id', 'body')
