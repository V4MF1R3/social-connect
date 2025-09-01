from django.urls import path
from .feed import FeedView

urlpatterns = [
    path('feed/', FeedView.as_view(), name='main-feed'),
]
