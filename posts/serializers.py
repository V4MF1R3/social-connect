from rest_framework import serializers
from .models import Post, Like, Comment

class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    category = serializers.ChoiceField(choices=Post.CATEGORY_CHOICES)
    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'author_username', 'created_at', 'updated_at', 'image_url', 'category', 'is_active', 'like_count', 'comment_count']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'author_username', 'post', 'created_at', 'is_active']
