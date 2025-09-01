
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
	CATEGORY_CHOICES = (
		('general', 'General'),
		('announcement', 'Announcement'),
		('question', 'Question'),
	)
	content = models.TextField(max_length=280)
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	image_url = models.URLField(blank=True, null=True)
	category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
	is_active = models.BooleanField(default=True)
	like_count = models.PositiveIntegerField(default=0)
	comment_count = models.PositiveIntegerField(default=0)

	def __str__(self):
		return f"Post by {self.author.username} ({self.category})"

class Like(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('user', 'post')

class Comment(models.Model):
	content = models.TextField(max_length=200)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
	created_at = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return f"Comment by {self.author.username}"
