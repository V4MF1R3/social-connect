from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']

    def validate_username(self, value):
        import re
        if not re.match(r'^[A-Za-z0-9_]{3,30}$', value):
            raise serializers.ValidationError('Username must be 3-30 characters, alphanumeric or underscore.')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=False
        )
        if not UserProfile.objects.filter(user=user).exists():
            UserProfile.objects.create(user=user)
        token = default_token_generator.make_token(user)
        verification_url = f"http://localhost:8000/api/auth/verify-email/?uid={user.id}&token={token}"
        send_mail(
            'Verify your email',
            f'Click the link to verify your account: {verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'bio', 'avatar_url', 'website', 'location', 'privacy', 'followers_count', 'following_count', 'posts_count', 'role']

    def get_followers_count(self, obj):
        from follows.models import Follow
        return Follow.objects.filter(following=obj.user).count()

    def get_following_count(self, obj):
        from follows.models import Follow
        return Follow.objects.filter(follower=obj.user).count()

    def get_posts_count(self, obj):
        return obj.user.posts.count()
