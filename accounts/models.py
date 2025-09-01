
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	ROLE_CHOICES = (
		('user', 'User'),
		('admin', 'Admin'),
	)
	PRIVACY_CHOICES = (
		('public', 'Public'),
		('private', 'Private'),
		('followers_only', 'Followers Only'),
	)
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
	bio = models.CharField(max_length=160, blank=True)
	avatar_url = models.URLField(blank=True)
	website = models.URLField(blank=True)
	location = models.CharField(max_length=100, blank=True)
	privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
	followers_count = models.PositiveIntegerField(default=0)
	following_count = models.PositiveIntegerField(default=0)
	posts_count = models.PositiveIntegerField(default=0)

	def __str__(self):
		return f"{self.user.username} Profile"
