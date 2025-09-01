from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Notification

class NotificationsTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='testuser', password='testpass')
		self.sender = User.objects.create_user(username='sender', password='senderpass')
		self.notification = Notification.objects.create(recipient=self.user, sender=self.sender, message='Test notification')

	def test_list_notifications(self):
		self.client.force_authenticate(user=self.user)
		url = reverse('get-notifications')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

	def test_mark_read(self):
		self.client.force_authenticate(user=self.user)
		url = reverse('mark-notification-read', args=[self.notification.id])
		response = self.client.patch(url)
		self.assertEqual(response.status_code, 200)
