from rest_framework import serializers
from django.contrib.auth.models import User
from posts.models import Post

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'date_joined', 'last_login']

class AdminPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'created_at', 'updated_at', 'is_active', 'like_count', 'comment_count', 'category']
