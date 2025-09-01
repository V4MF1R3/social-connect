from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Post
from django.core.files.uploadedfile import SimpleUploadedFile

class PostsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(author=self.user, content='Hello world!')

    def test_create_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-list-create')
        image = SimpleUploadedFile(
            name='test.jpg',
            content=b'\xff\xd8\xff\xe0' + b'\x00' * 100,  # Minimal valid JPEG header
            content_type='image/jpeg'
        )
        data = {
            'content': 'New post with image',
            'category': 'general',
            'image': image,
        }
        response = self.client.post(url, data, format='multipart')
        print('Create post response:', response.data)
        self.assertIn(response.status_code, [201, 200])

    def test_like_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('like-post', args=[self.post.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

