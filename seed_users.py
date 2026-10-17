import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
try:
    from apps.messaging.rabbitmq import publish_event
except Exception:
    publish_event = None

User = get_user_model()

def seed_users():
    users_data = [
        {
            'id': '11111111-1111-4111-8111-111111111111',
            'username': 'ahmed',
            'first_name': 'Ahmed',
            'last_name': 'Al-Mansoor',
            'email': 'ahmed@company.com',
            'password': 'password123',
            'job_title': 'Lead Architect & Engineering Director',
        },
        {
            'id': '22222222-2222-4222-8222-222222222222',
            'username': 'mohammed',
            'first_name': 'Mohammed',
            'last_name': 'Al-Sayed',
            'email': 'mohammed@company.com',
            'password': 'password123',
            'job_title': 'Senior Full Stack Developer',
        },
        {
            'id': '33333333-3333-4333-8333-333333333333',
            'username': 'khaled',
            'first_name': 'Khaled',
            'last_name': 'Al-Rashid',
            'email': 'khaled@company.com',
            'password': 'password123',
            'job_title': 'DevOps & Infrastructure Lead',
        },
        {
            'id': '44444444-4444-4444-8444-444444444444',
            'username': 'tariq',
            'first_name': 'Tariq',
            'last_name': 'Al-Harbi',
            'email': 'tariq@company.com',
            'password': 'password123',
            'job_title': 'QA Automation Specialist',
        },
        {
            'id': '55555555-5555-4555-8555-555555555555',
            'username': 'sarah',
            'first_name': 'Sarah',
            'last_name': 'Al-Otaibi',
            'email': 'sarah@company.com',
            'password': 'password123',
            'job_title': 'Product Manager & UX Lead',
        },
        {
            'id': '66666666-6666-4666-8666-666666666666',
            'username': 'fahad',
            'first_name': 'Fahad',
            'last_name': 'Al-Ghamdi',
            'email': 'fahad@company.com',
            'password': 'password123',
            'job_title': 'Junior Frontend Developer',
        },
    ]

    print("\n=======================================================")
    print(" [1/4] Seeding Users in User Management Service...")
    print("=======================================================")
    for data in users_data:
        uid = data['id']
        username = data['username']
        password = data['password']
        email = data['email']
        first_name = data['first_name']
        last_name = data['last_name']
        job_title = data['job_title']

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'outer_id': uid,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        user.outer_id = uid
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.save()

        full_name = f"{first_name} {last_name}".strip()
        outer_id_str = str(getattr(user, 'outer_id', uid))
        if publish_event:
            try:
                publish_event('user.created', {
                    'id': user.id,
                    'outer_id': outer_id_str,
                    'user_id': outer_id_str,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': full_name,
                    'email': user.email,
                    'job_title': job_title,
                })
            except Exception:
                pass
        print(f" -> {'[Created]' if created else '[Updated]'} User: {username} ({full_name}) - ID: {user.id}, Outer ID: {outer_id_str}")

    print(" -> User seeding successfully completed.\n")

if __name__ == '__main__':
    seed_users()
