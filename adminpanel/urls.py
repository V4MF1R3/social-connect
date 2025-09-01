from django.urls import path
from .views import (
    AdminUserListView, AdminUserDetailView, AdminUserDeactivateView,
    AdminPostListView, AdminDeletePostView, AdminStatsView
)

urlpatterns = [
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/<int:pk>/deactivate/', AdminUserDeactivateView.as_view(), name='admin-user-deactivate'),
    path('admin/posts/', AdminPostListView.as_view(), name='admin-post-list'),
    path('admin/posts/<int:pk>/', AdminDeletePostView.as_view(), name='admin-post-delete'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
]
