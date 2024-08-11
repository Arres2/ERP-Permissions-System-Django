from rest_framework import viewsets, status
from rest_framework.decorators import action
from .decorators import check_module_permission
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Module, Permission, Role, UserRole, UserPermission
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer, ModuleSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
# from django.utils.decorators import method_decorator
# from django.core.cache import cache
# from django.views.decorators.cache import cache_page
# from django_redis import get_redis_connection
# from django.core.mail import send_mail
# from django.conf import settings
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
from rest_framework import status


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def verify_email(request, token):
#     try:
#         profile = UserSerializer.objects.get(email_verification_token=token)
#         if not profile.email_verified:
#             profile.email_verified = True
#             profile.save()
#             return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
#         else:
#             return Response({"message": "Email already verified"}, status=status.HTTP_200_OK)
#     except UserSerializer.DoesNotExist:
#         return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)



class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        user = self.get_object()
        role_id = request.data.get('role_id')
        try:
            role = Role.objects.get(id=role_id)
            UserRole.objects.create(user=user, role=role)
            return Response({'status': 'role assigned'})
        except Role.DoesNotExist:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def assign_permission(self, request, pk=None):
        user = self.get_object()
        permission_id = request.data.get('permission_id')
        module_id = request.data.get('module_id')
        try:
            permission = Permission.objects.get(id=permission_id)
            module = Module.objects.get(id=module_id)
            UserPermission.objects.create(user=user, permission=permission, module=module)
            return Response({'status': 'permission assigned'})
        except (Permission.DoesNotExist, Module.DoesNotExist):
            return Response({'error': 'Permission or Module not found'}, status=status.HTTP_404_NOT_FOUND)
        
    @check_module_permission('create_user', 'user_management')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # user = serializer.save()
        
        # Send verification email
        # token = user.userprofile.email_verification_token
        # verification_link = f"{settings.SITE_URL}/verify-email/{token}/"
        # send_mail(
        #     'Verify your email',
        #     f'Please click this link to verify your email: {verification_link}',
        #     settings.DEFAULT_FROM_EMAIL,
        #     [user.email],
        #     fail_silently=False,
        # )
        
        # return Response({
        #     "user": UserSerializer(user, context=self.get_serializer_context()).data,
        #     "message": "User Created Successfully. Please check your email to verify your account.",
        # }, status=status.HTTP_201_CREATED)

    # @method_decorator(cache_page(60*15))  # Cache for 15 minutes
    @action(detail=True, methods=['get'])
    def check_permission(self, request, pk=None):
        user = self.get_object()
        permission_name = request.query_params.get('permission')
        module_name = request.query_params.get('module')
        
        has_permission = UserPermission.objects.filter(
            user=user,
            permission__name=permission_name,
            module__name=module_name
        ).exists() or UserRole.objects.filter(
            user=user,
            role__permissions__name=permission_name
        ).exists()
        
        return Response({'has_permission': has_permission})

    def get_permissions(self):
        # cache_key = f"user_permissions_{self.request.user.id}"
        # permissions = cache.get(cache_key)
        # if permissions is None:
        permissions = UserPermission.objects.filter(user=self.request.user).select_related('permission', 'module')
            # cache.set(cache_key, permissions, 60*60)  # Cache for 1 hour
        return permissions
    
    
    # @action(detail=True, methods=['get'])
    # def get_user_stats(self, request, pk=None):
    #     user = self.get_object()
    #     redis_conn = get_redis_connection("default")
        
    #     # Increment login count
    #     login_count = redis_conn.incr(f"user:{user.id}:login_count")
        
    #     # Add to recent users set
    #     redis_conn.zadd("recent_users", {user.id: int(time.time())})
        
    #     # Get user's rank
    #     user_rank = redis_conn.zrevrank("recent_users", user.id)
        
    #     return Response({
    #         "login_count": login_count,
    #         "recent_user_rank": user_rank
    #     })

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer