from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.conf import settings
from common_permissions import IsOwnerOrReadOnly
from .models import Post, Like, Comment
from .serializers import PostSerializer, LikeSerializer, CommentSerializer
import logging
from supabase import create_client
import re

class PostListCreateView(generics.ListCreateAPIView):
	queryset = Post.objects.filter(is_active=True).order_by('-created_at')
	serializer_class = PostSerializer
	permission_classes = [permissions.IsAuthenticated]
	parser_classes = [MultiPartParser, FormParser]

	def perform_create(self, serializer):
		image = self.request.FILES.get('image')
		image_url = None
		if image:
			# Validate file type and size
			if image.content_type not in ['image/jpeg', 'image/png']:
				raise serializers.ValidationError('Only JPEG and PNG images are allowed.')
			if image.size > 2 * 1024 * 1024:
				raise serializers.ValidationError('Max file size is 2MB.')
			# Upload to Supabase Storage
			supabase_url = settings.SUPABASE_URL
			supabase_key = settings.SUPABASE_KEY
			supabase = create_client(supabase_url, supabase_key)
			file_path = f"posts/{self.request.user.username}_{image.name}"
			try:
				res = supabase.storage.from_('posts').upload(file_path, image.read())
				if hasattr(res, 'error') and res.error:
					logging.error(f"Supabase upload error: {res.error}")
					raise serializers.ValidationError(f'Failed to upload image: {res.error}')
				image_url = supabase.storage.from_('posts').get_public_url(file_path)
			except Exception as e:
				logging.exception("Exception during image upload:")
				raise serializers.ValidationError(f'Image upload failed: {str(e)}')
		try:
			serializer.save(author=self.request.user, image_url=image_url, is_active=True)
		except Exception as e:
			logging.exception("Exception during serializer.save():")
			raise serializers.ValidationError(f'Post creation failed: {str(e)}')

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()
		image_url = getattr(instance, 'image_url', None)
		# Delete image from Supabase storage if it exists
		if image_url:
			supabase_url = settings.SUPABASE_URL
			supabase_key = settings.SUPABASE_KEY
			supabase = create_client(supabase_url, supabase_key)
			# Extract the file path from the public URL
			match = re.search(r'/storage/v1/object/public/posts/(.+)$', image_url)
			if match:
				file_path = match.group(1)
				try:
					res = supabase.storage.from_('posts').remove([file_path])
					if hasattr(res, 'error') and res.error:
						logging.error(f"Supabase delete error: {res.error}")
				except Exception as e:
					logging.exception("Exception during image delete from Supabase:")
		return super().destroy(request, *args, **kwargs)
	queryset = Post.objects.filter(is_active=True)
	serializer_class = PostSerializer
	def get_permissions(self):
		if self.request.method in ['PUT', 'PATCH', 'DELETE']:
			# Only owner or admin can edit/delete
			if self.request.user.profile.role == 'admin':
				return [permissions.IsAuthenticated()]
			return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
		return [permissions.IsAuthenticated()]


# Combined Like/Unlike view
from rest_framework.views import APIView

class LikeUnlikePostView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, post_id):
		post = Post.objects.get(id=post_id)
		like, created = Like.objects.get_or_create(user=request.user, post=post)
		if created:
			post.like_count += 1
			post.save()
			return Response({'message': 'Post liked.'})
		return Response({'message': 'Already liked.'}, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, post_id):
		post = Post.objects.get(id=post_id)
		like = Like.objects.filter(user=request.user, post=post).first()
		if like:
			like.delete()
			post.like_count = max(0, post.like_count - 1)
			post.save()
			return Response({'message': 'Post unliked.'})
		return Response({'message': 'Not liked yet.'}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView

class PostCommentsView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, post_id):
		comments = Comment.objects.filter(post_id=post_id, is_active=True)
		serializer = CommentSerializer(comments, many=True)
		return Response(serializer.data)

	def post(self, request, post_id):
		post = Post.objects.get(id=post_id)
		data = request.data.copy()
		data.pop('author', None)
		data.pop('post', None)
		serializer = CommentSerializer(data=data)
		if serializer.is_valid():
			serializer.save(author=request.user, post=post)
			post.comment_count += 1
			post.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteCommentView(generics.DestroyAPIView):
	serializer_class = CommentSerializer
	permission_classes = [permissions.IsAuthenticated]

	def delete(self, request, comment_id):
		comment = Comment.objects.filter(id=comment_id, author=request.user).first()
		if comment:
			comment.is_active = False
			comment.save()
			return Response({'message': 'Comment deleted.'})
		return Response({'message': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
from django.shortcuts import render

# Create your views here.
