import os
import logging
import requests
from django.db.transaction import set_rollback
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.messaging.rabbitmq import publish_event

User = get_user_model()
logger = logging.getLogger(__name__)

class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        outer_id_str = str(getattr(user, 'outer_id', user.id))
        token['username'] = user.username
        token['email'] = user.email
        token['full_name'] = full_name
        token['user_id'] = outer_id_str
        token['user_num_id'] = user.id

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['expires_in'] = int(settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME').total_seconds())
        user = self.user
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        outer_id_str = str(getattr(user, 'outer_id', user.id))
        data['user'] = {
            'outer_id': outer_id_str,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': full_name,
        }
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, min_length=4, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    job_title = serializers.CharField(write_only=True, required=True)
    department = serializers.CharField(write_only=True, required=False, default='General')
    phone = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True, default=None)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'department', 'job_title', 'phone']

    @transaction.atomic()
    def create(self, validated_data):
        department = validated_data.pop('department', 'General')
        job_title = validated_data.pop('job_title', 'Team Member')
        phone = validated_data.pop('phone', None) or None
        email = validated_data.get('email')
        validated_data['email'] = email.strip() if email else None
        password = validated_data.pop('password')

        user = User.objects.create_user(password=password, **validated_data)
        
        outer_id_str = str(getattr(user, 'outer_id', user.id))
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username

        payload = {
            'id': user.id,
            'outer_id': outer_id_str,
            'user_id': outer_id_str,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': full_name,
            'email': user.email,
            'department': department,
            'job_title': job_title,
            'phone': phone,
        }

        # Dispatch Celery task to employee-service to create the employee profile
        from config.celery import celery_app
        try:
            celery_app.send_task(
                'apps.employees.tasks.create_employee_profile',
                args=[payload],
                queue='celery'
            )
            logger.info(f"[Celery] Dispatched create_employee_profile task for '{user.username}'")
        except Exception as exc:
            logger.warning(f"[Celery] Failed to dispatch create_employee_profile task: {exc}")

        # Also publish user.created event via Celery/Kombu for topic subscribers
        publish_event('user.created', payload)
        return user
