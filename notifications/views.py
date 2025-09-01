from rest_framework import generics, permissions, status
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.response import Response

class NotificationListView(generics.ListAPIView):
	serializer_class = NotificationSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

class MarkNotificationReadView(generics.UpdateAPIView):
	serializer_class = NotificationSerializer
	permission_classes = [permissions.IsAuthenticated]
	queryset = Notification.objects.all()

	def update(self, request, *args, **kwargs):
		notification = self.get_object()
		notification.is_read = True
		notification.save()
		return Response({'message': 'Notification marked as read.'})

class MarkAllNotificationsReadView(generics.GenericAPIView):
	permission_classes = [permissions.IsAuthenticated]
	def post(self, request):
		Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
		return Response({'message': 'All notifications marked as read.'})
 # Imports cleaned up for maintainability
