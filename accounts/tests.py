from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import UserProfile

class AccountsTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='testuser', password='testpass', email='test@example.com')
		self.profile = UserProfile.objects.create(user=self.user)


	def test_login(self):
		url = reverse('token_obtain_pair')
		data = {'username': 'testuser', 'password': 'testpass'}
		response = self.client.post(url, data)
		self.assertEqual(response.status_code, 200)

		self.client.force_authenticate(user=self.user)
		url = reverse('profile')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
