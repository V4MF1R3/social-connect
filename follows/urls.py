from django.urls import path
from .views import FollowUnfollowUserView, GetFollowersView, GetFollowingView

urlpatterns = [
    path('users/<int:user_id>/follow/', FollowUnfollowUserView.as_view(), name='follow-unfollow-user'),
    path('users/<int:user_id>/followers/', GetFollowersView.as_view(), name='get-followers'),
    path('users/<int:user_id>/following/', GetFollowingView.as_view(), name='get-following'),
]
