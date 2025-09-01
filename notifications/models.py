
from django.db import models
from django.contrib.auth.models import User
from posts.models import Post

class Notification(models.Model):
	NOTIFICATION_TYPES = (
		('follow', 'Follow'),
		('like', 'Like'),
		('comment', 'Comment'),
	)
	recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
	sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
	notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
	message = models.CharField(max_length=200)
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.notification_type} from {self.sender.username} to {self.recipient.username}"
