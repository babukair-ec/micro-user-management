import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.messaging.rabbitmq import publish_event

def seed_users():
    users_data = [
        {
            'id': 1,
            'username': 'ahmed',
            'first_name': 'Ahmed',
            'last_name': 'Al-Mansoor',
            'email': 'ahmed@company.com',
            'password': 'password123',
            'department': 'Backend Engineering',
            'job_title': 'Senior Software Engineer',
        },
        {
            'id': 2,
            'username': 'mohammed',
            'first_name': 'Mohammed',
            'last_name': 'Al-Sayed',
            'email': 'mohammed@company.com',
            'password': 'password123',
            'department': 'Product Development',
            'job_title': 'Full Stack Developer',
        },
        {
            'id': 3,
            'username': 'khaled',
            'first_name': 'Khaled',
            'last_name': 'Al-Rashid',
            'email': 'khaled@company.com',
            'password': 'password123',
            'department': 'DevOps & Reliability',
            'job_title': 'Systems Engineer',
        },
        {
            'id': 4,
            'username': 'tariq',
            'first_name': 'Tariq',
            'last_name': 'Al-Harbi',
            'email': 'tariq@company.com',
            'password': 'password123',
            'department': 'Quality Assurance',
            'job_title': 'QA Automation Specialist',
        },
    ]

    print("Seeding users in User Management Microservice...")
    for data in users_data:
        uid = data['id']
        username = data['username']
        password = data['password']
        email = data['email']
        first_name = data['first_name']
        last_name = data['last_name']
        department = data['department']
        job_title = data['job_title']

        user, created = User.objects.get_or_create(
            id=uid,
            defaults={
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.save()

        full_name = f"{first_name} {last_name}".strip()
        publish_event('user.created', {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': full_name,
            'email': user.email,
            'department': department,
            'job_title': job_title,
        })
        print(f"[{'Created' if created else 'Updated'}] User: {username} (ID: {user.id})")

    print("User seeding completed.")

if __name__ == '__main__':
    seed_users()
