
from django.db import models
from django.contrib.auth.models import User

class Follow(models.Model):
	follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
	following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('follower', 'following')

	def __str__(self):
		return f"{self.follower.username} follows {self.following.username}"
