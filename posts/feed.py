from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Post
from follows.models import Follow
from .serializers import PostSerializer

class FeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        following_ids = list(Follow.objects.filter(follower=user).values_list('following_id', flat=True))
        post_queryset = Post.objects.filter(author_id__in=following_ids + [user.id], is_active=True).order_by('-created_at')
        page = int(request.GET.get('page', 1))
        page_size = 20
        start = (page - 1) * page_size
        end = start + page_size
        posts = post_queryset[start:end]
        results = []
        for post in posts:
            data = PostSerializer(post).data
            # User interaction status
            data['liked'] = post.likes.filter(user=user).exists()
            data['commented'] = post.comments.filter(author=user).exists()
            results.append(data)
        return Response({
            'results': results,
            'page': page,
            'total': post_queryset.count(),
        })
