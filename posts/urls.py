from django.urls import path
from .views import (
    PostListCreateView, PostDetailView,
    LikeUnlikePostView,
    PostCommentsView, DeleteCommentView
)

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/like/', LikeUnlikePostView.as_view(), name='like-unlike-post'),
    path('posts/<int:post_id>/comments/', PostCommentsView.as_view(), name='post-comments'),
    path('comments/<int:comment_id>/', DeleteCommentView.as_view(), name='delete-comment'),
]
