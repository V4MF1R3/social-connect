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
 # ...existing code...
 # Imports cleaned up for maintainability

class RegisterView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = UserRegisterSerializer
	permission_classes = [permissions.AllowAny]

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
		# If accessing own profile, always allow
		if str(self.kwargs.get('pk', '')) == str(self.request.user.profile.pk):
			return self.request.user.profile
		# Otherwise, check privacy
		profile = UserProfile.objects.get(pk=self.kwargs.get('pk')) if self.kwargs.get('pk') else self.request.user.profile
		if profile.privacy == 'public':
			return profile
		elif profile.privacy == 'private':
			if profile.user == self.request.user:
				return profile
			else:
				from rest_framework.exceptions import PermissionDenied
				raise PermissionDenied('This profile is private.')
		elif profile.privacy == 'followers_only':
			if profile.user == self.request.user:
				return profile
			# Check if current user follows this user
			from follows.models import Follow
			if Follow.objects.filter(follower=self.request.user, following=profile.user).exists():
				return profile
			else:
				from rest_framework.exceptions import PermissionDenied
				raise PermissionDenied('This profile is only visible to followers.')
		return profile

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
