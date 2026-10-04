from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from apps.messaging.rabbitmq import publish_event

class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        token['username'] = user.username
        token['email'] = user.email
        token['full_name'] = full_name
        token['employee_id'] = user.id
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': full_name,
        }
        data['employee'] = {
            'id': user.id,
            'user_id': user.id,
            'username': user.username,
            'full_name': full_name,
            'email': user.email,
        }
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)
    department = serializers.CharField(write_only=True, required=False, default='General')
    job_title = serializers.CharField(write_only=True, required=False, default='Team Member')
    phone = serializers.CharField(write_only=True, required=False, default='')

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'department', 'job_title', 'phone']

    def create(self, validated_data):
        department = validated_data.pop('department', 'General')
        job_title = validated_data.pop('job_title', 'Team Member')
        phone = validated_data.pop('phone', '')
        password = validated_data.pop('password')

        user = User.objects.create_user(password=password, **validated_data)
        
        # Publish user.created event for Employee service and other consumers
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        publish_event('user.created', {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': full_name,
            'email': user.email,
            'department': department,
            'job_title': job_title,
            'phone': phone,
        })
        return user
