from rest_framework import generics, permissions, status
from .models import Follow
from .serializers import FollowSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response


from rest_framework.views import APIView

class FollowUnfollowUserView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, user_id):
		following = User.objects.get(id=user_id)
		if following == request.user:
			return Response({'error': 'Cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
		follow, created = Follow.objects.get_or_create(follower=request.user, following=following)
		if created:
			return Response({'message': 'User followed.'})
		return Response({'message': 'Already following.'}, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, user_id):
		following = User.objects.get(id=user_id)
		follow = Follow.objects.filter(follower=request.user, following=following).first()
		if follow:
			follow.delete()
			return Response({'message': 'User unfollowed.'})
		return Response({'message': 'Not following.'}, status=status.HTTP_400_BAD_REQUEST)

class GetFollowersView(generics.ListAPIView):
	serializer_class = FollowSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		user_id = self.kwargs['user_id']
		return Follow.objects.filter(following_id=user_id)

class GetFollowingView(generics.ListAPIView):
	serializer_class = FollowSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		user_id = self.kwargs['user_id']
		return Follow.objects.filter(follower_id=user_id)
from django.shortcuts import render

# Create your views here.
