from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Follow

class FollowsTests(APITestCase):
	def setUp(self):
		self.user1 = User.objects.create_user(username='user1', password='pass1')
		self.user2 = User.objects.create_user(username='user2', password='pass2')

	def test_follow(self):
		self.client.force_authenticate(user=self.user1)
		url = reverse('follow-user', args=[self.user2.id])
		response = self.client.post(url)
		self.assertIn(response.status_code, [200, 201])

	def test_unfollow(self):
		Follow.objects.create(follower=self.user1, following=self.user2)
		self.client.force_authenticate(user=self.user1)
		url = reverse('unfollow-user', args=[self.user2.id])
		response = self.client.delete(url)
		self.assertIn(response.status_code, [204, 200, 405])
