from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile
from posts.models import Post

class AdminPanelTests(APITestCase):
	def setUp(self):
		self.admin = User.objects.create_user(username='admin', password='adminpass')
		UserProfile.objects.create(user=self.admin, role='admin')
		self.user = User.objects.create_user(username='user', password='userpass')
		self.post = Post.objects.create(author=self.user, content='Admin test post')

	def test_admin_user_list(self):
		self.client.force_authenticate(user=self.admin)
		url = reverse('admin-user-list')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

	def test_admin_post_list(self):
		self.client.force_authenticate(user=self.admin)
		url = reverse('admin-post-list')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
