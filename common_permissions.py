from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admin to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Allow if user is admin
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return True
        # Allow if user is owner
        return getattr(obj, 'user', None) == request.user or getattr(obj, 'author', None) == request.user
