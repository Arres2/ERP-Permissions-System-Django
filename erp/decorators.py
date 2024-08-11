from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .models import UserPermission, UserRole

def check_module_permission(permission_name, module_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            user = request.user
            if user.is_superuser:
                return view_func(self, request, *args, **kwargs)
            
            has_permission = UserPermission.objects.filter(
                user=user,
                permission__name=permission_name,
                module__name=module_name
            ).exists() or UserRole.objects.filter(
                user=user,
                role__permissions__name=permission_name
            ).exists()
            
            if has_permission:
                return view_func(self, request, *args, **kwargs)
            else:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        return _wrapped_view
    return decorator