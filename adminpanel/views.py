from rest_framework import generics, permissions, status
from django.contrib.auth.models import User
from posts.models import Post
from .serializers import AdminUserSerializer, AdminPostSerializer
from rest_framework.response import Response
from accounts.models import UserProfile

class IsAdminUser(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'admin'

class AdminUserListView(generics.ListAPIView):
	serializer_class = AdminUserSerializer
	permission_classes = [IsAdminUser]

	def get_queryset(self):
		queryset = User.objects.all()
		search = self.request.GET.get('search')
		if search:
			queryset = queryset.filter(username__icontains=search)
		return queryset

class AdminUserDetailView(generics.RetrieveAPIView):
	serializer_class = AdminUserSerializer
	permission_classes = [IsAdminUser]
	queryset = User.objects.all()

class AdminUserDeactivateView(generics.UpdateAPIView):
	serializer_class = AdminUserSerializer
	permission_classes = [IsAdminUser]
	queryset = User.objects.all()

	def update(self, request, *args, **kwargs):
		user = self.get_object()
		user.is_active = False
		user.save()
		return Response({'message': 'User deactivated.'})

class AdminPostListView(generics.ListAPIView):
	serializer_class = AdminPostSerializer
	permission_classes = [IsAdminUser]
	queryset = Post.objects.all()

class AdminDeletePostView(generics.DestroyAPIView):
	serializer_class = AdminPostSerializer
	permission_classes = [IsAdminUser]
	queryset = Post.objects.all()

class AdminStatsView(generics.GenericAPIView):
	permission_classes = [IsAdminUser]
	def get(self, request):
		total_users = User.objects.count()
		total_posts = Post.objects.count()
		# Handle case where last_login is None
		if request.user.last_login:
			active_today = User.objects.filter(last_login__date=request.user.last_login.date()).count()
		else:
			active_today = 0
		return Response({
			'total_users': total_users,
			'total_posts': total_posts,
			'active_today': active_today,
		})
from django.shortcuts import render

# Create your views here.
