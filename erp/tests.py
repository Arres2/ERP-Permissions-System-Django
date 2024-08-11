# security/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Role, Permission, Module

class UserAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_create_user(self):
        data = {
            "username": "newuser",
            "password": "newpass123",
            "password2": "newpass123",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User"
        }
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_assign_role(self):
        role = Role.objects.create(name='TestRole')
        response = self.client.post(f'/api/users/{self.user.id}/assign_role/', {'role_id': role.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_permission(self):
        module = Module.objects.create(name='TestModule')
        permission = Permission.objects.create(name='TestPermission')
        self.user.userpermission_set.create(permission=permission, module=module)
        
        response = self.client.get(f'/api/users/{self.user.id}/check_permission/?permission=TestPermission&module=TestModule')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_permission'])

# Ejecuta las pruebas con: python manage.py test security