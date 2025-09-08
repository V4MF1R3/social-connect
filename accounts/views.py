# View another user's profile with privacy logic
from .models import UserProfile
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class UserProfileDetailView(APIView):
	def get(self, request, user_id):
		try:
			user = User.objects.get(id=user_id)
			profile = UserProfile.objects.get(user=user)
		except (User.DoesNotExist, UserProfile.DoesNotExist):
			return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
		# Privacy logic
		request_user = request.user if request.user.is_authenticated else None
		allowed = False
		if profile.privacy == 'public':
			allowed = True
		elif profile.privacy == 'private':
			allowed = (request_user == user)
		elif profile.privacy == 'followers_only':
			if request_user == user:
				allowed = True
			else:
				from follows.models import Follow
				allowed = request_user and Follow.objects.filter(follower=request_user, following=user).exists()
		# Always show avatar and username
		data = {
			'id': profile.id,
			'username': user.username,
			'avatar_url': profile.avatar_url,
		}
		if allowed:
			from .serializers import UserProfileSerializer
			data.update(UserProfileSerializer(profile).data)
		return Response(data)
from rest_framework import permissions
# User Search Endpoint
from rest_framework import generics, filters
from django.contrib.auth.models import User
from .serializers import UserRegisterSerializer

class UserSearchView(generics.ListAPIView):
	queryset = User.objects.all()
	serializer_class = UserRegisterSerializer
	filter_backends = [filters.SearchFilter]
	search_fields = ['username', 'email', 'first_name', 'last_name']
	permission_classes = [permissions.IsAuthenticated]
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status

from common_permissions import IsOwnerOrReadOnly

class VerifyEmailView(generics.GenericAPIView):
	permission_classes = [permissions.AllowAny]
	def get(self, request):
		uid = request.GET.get('uid')
		token = request.GET.get('token')
		try:
			user = User.objects.get(id=uid)
		except User.DoesNotExist:
			return Response({'error': 'Invalid user.'}, status=400)
		if default_token_generator.check_token(user, token):
			user.is_active = True
			user.save()
			return Response({'message': 'Email verified. Account activated.'})
		return Response({'error': 'Invalid or expired token.'}, status=400)
from .models import UserProfile
from .serializers import UserRegisterSerializer, UserProfileSerializer
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

class PasswordResetView(generics.GenericAPIView):
	permission_classes = [permissions.AllowAny]
	def post(self, request):
		email = request.data.get('email')
		user = User.objects.filter(email=email).first()
		if user:
			token = default_token_generator.make_token(user)
			reset_url = f"http://localhost:8000/api/auth/password-reset-confirm/?email={email}&token={token}"
			send_mail(
				'Password Reset',
				f'Click the link to reset your password: {reset_url}',
				'noreply@socialconnect.com',
				[email],
				fail_silently=True
			)
			return Response({'message': 'Password reset email sent.'})
		return Response({'error': 'User not found.'}, status=404)

class PasswordResetConfirmView(generics.GenericAPIView):
	permission_classes = [permissions.AllowAny]
	def post(self, request):
		email = request.data.get('email')
		token = request.data.get('token')
		new_password = request.data.get('new_password')
		user = User.objects.filter(email=email).first()
		if user and default_token_generator.check_token(user, token):
			user.password = make_password(new_password)
			user.save()
			return Response({'message': 'Password reset successful.'})
		return Response({'error': 'Invalid token or user.'}, status=400)

class ChangePasswordView(generics.UpdateAPIView):
	permission_classes = [permissions.IsAuthenticated]
	def update(self, request, *args, **kwargs):
		user = request.user
		old_password = request.data.get('old_password')
		new_password = request.data.get('new_password')
		if not user.check_password(old_password):
			return Response({'error': 'Old password is incorrect.'}, status=400)
		user.set_password(new_password)
		user.save()
		return Response({'message': 'Password changed successfully.'})
 

class RegisterView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = UserRegisterSerializer
	permission_classes = [permissions.AllowAny]

	def perform_create(self, serializer):
		user = serializer.save(is_active=False)
		token = default_token_generator.make_token(user)
		verify_url = f"https://social-connect-frontend-gamma.vercel.app/verify-email?uid={user.id}&token={token}"
		send_mail(
			'Verify your email',
			f'Click the link to verify your account: {verify_url}',
			'noreply@socialconnect.com',
			[user.email],
			fail_silently=True
		)

class ProfileView(generics.RetrieveUpdateAPIView):
	queryset = UserProfile.objects.all()
	serializer_class = UserProfileSerializer
	def get_permissions(self):
		user = self.request.user
		if self.request.method in ['PUT', 'PATCH', 'DELETE']:
			# Only owner or admin can edit/delete
			if not user.is_authenticated:
				return [permissions.IsAuthenticated()]
			if hasattr(user, 'profile') and getattr(user.profile, 'role', None) == 'admin':
				return [permissions.IsAuthenticated()]
			return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
		return [permissions.IsAuthenticated()]


	def get_object(self):
		# Always allow avatar_url and username to be visible
		from rest_framework.exceptions import PermissionDenied
		profile = UserProfile.objects.get(pk=self.kwargs.get('pk')) if self.kwargs.get('pk') else self.request.user.profile
		request_user = self.request.user
		# If accessing own profile, always allow
		if str(self.kwargs.get('pk', '')) == str(request_user.profile.pk):
			return profile
		# For public profiles, allow all fields
		if profile.privacy == 'public':
			return profile
		# For private or followers_only, return a partial profile for non-allowed users
		allowed = False
		if profile.privacy == 'private':
			allowed = profile.user == request_user
		elif profile.privacy == 'followers_only':
			if profile.user == request_user:
				allowed = True
			else:
				from follows.models import Follow
				allowed = Follow.objects.filter(follower=request_user, following=profile.user).exists()
		if allowed:
			return profile
		# Return a partial profile with only avatar_url and username
		class PartialProfile:
			def __init__(self, profile):
				self.id = profile.id
				self.avatar_url = profile.avatar_url
				self.user = profile.user
				self.username = profile.user.username
		return PartialProfile(profile)

	def update(self, request, *args, **kwargs):
		import logging
		logger = logging.getLogger(__name__)
		profile = self.get_object()
		avatar = request.FILES.get('avatar')
		if avatar:
			# Validate file type and size
			if avatar.content_type not in ['image/jpeg', 'image/png']:
				return Response({'error': 'Only JPEG and PNG images are allowed.'}, status=400)
			if avatar.size > 2 * 1024 * 1024:
				return Response({'error': 'Max file size is 2MB.'}, status=400)
			# Upload to Supabase Storage
			from supabase import create_client
			from django.conf import settings
			supabase_url = settings.SUPABASE_URL
			supabase_key = settings.SUPABASE_KEY
			supabase = create_client(supabase_url, supabase_key)
			# Delete old avatar if exists
			old_avatar_url = getattr(profile, 'avatar_url', None)
			import re
			if old_avatar_url:
				match = re.search(r'/storage/v1/object/public/avatars/(.+)$', old_avatar_url)
				if match:
					old_file_path = match.group(1)
					try:
						res_del = supabase.storage.from_('avatars').remove([old_file_path])
						logger.info(f"Supabase old avatar delete response: {res_del}")
						if hasattr(res_del, 'error') and res_del.error:
							logger.error(f"Supabase delete error: {res_del.error}")
					except Exception as e:
						logger.exception(f"Exception during old avatar delete: {e}")
			file_path = f"avatars/{profile.user.username}_{avatar.name}"
			try:
				res = supabase.storage.from_('avatars').update(file_path, avatar.read())
				logger.info(f"Supabase upload response: {res}")
				if hasattr(res, 'error') and res.error:
					logger.error(f"Supabase upload error: {res.error}")
					return Response({'error': 'Failed to upload avatar.'}, status=400)
				public_url = supabase.storage.from_('avatars').get_public_url(file_path)
				logger.info(f"Supabase public URL: {public_url}")
				if not public_url:
					logger.error("Public URL for avatar is empty or None.")
					return Response({'error': 'Failed to retrieve avatar URL.'}, status=400)
				profile.avatar_url = public_url
			except Exception as e:
				logger.exception(f"Exception during avatar upload: {e}")
				return Response({'error': 'Avatar upload failed. Please try again later.'}, status=400)
		# Update other fields
		for field in ['bio', 'website', 'location', 'privacy']:
			if field in request.data:
				setattr(profile, field, request.data[field])
		try:
			profile.save()
		except Exception as e:
			logger.exception(f"Exception during profile save: {e}")
			return Response({'error': 'Failed to save profile.'}, status=400)
		serializer = self.get_serializer(profile)
		return Response(serializer.data)
from django.shortcuts import render

# Create your views here.
