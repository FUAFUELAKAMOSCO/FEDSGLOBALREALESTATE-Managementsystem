from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Provision and ensure all Fred's Global Real Estate worker accounts exist with valid credentials"

    def handle(self, *args, **options):
        workers = [
            {
                'username': 'fred_manager',
                'first_name': 'Fred',
                'last_name': 'Nguemo',
                'role': 'CEO',
                'email': 'fred@fredsglobalrealestate.com',
                'phone': '+237 679 798 244',
                'is_staff': True,
                'is_superuser': False,
            },
            {
                'username': 'fuafuelakamosco',
                'first_name': 'Fuafuelaka',
                'last_name': 'Mosco',
                'role': 'ADMIN',
                'email': 'fuafuelakamosco@gmail.com',
                'phone': '+237 671 000 111',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'Tanyamiranda',
                'first_name': 'Miranda',
                'last_name': 'Tanya',
                'role': 'SECRETARIAT',
                'email': 'tanyamiranda@gmail.com',
                'phone': '+237 680 897 563',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'username': 'sarah_mbi',
                'first_name': 'Sarah',
                'last_name': 'Mbi',
                'role': 'AGENT',
                'email': 'sarah.mbi@fredsglobalrealestate.com',
                'phone': '+237 671 234 567',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'username': 'david_kamga',
                'first_name': 'David',
                'last_name': 'Kamga',
                'role': 'AGENT',
                'email': 'david.kamga@fredsglobalrealestate.com',
                'phone': '+237 692 345 678',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'username': 'field_manager',
                'first_name': 'Eric',
                'last_name': 'Tambe',
                'role': 'FIELD_MANAGER',
                'email': 'eric.tambe@fredsglobalrealestate.com',
                'phone': '+237 677 334 455',
                'is_staff': True,
                'is_superuser': False,
            },
            {
                'username': 'financial_manager',
                'first_name': 'Grace',
                'last_name': 'Fokam',
                'role': 'FINANCIAL',
                'email': 'grace.fokam@fredsglobalrealestate.com',
                'phone': '+237 699 556 677',
                'is_staff': True,
                'is_superuser': False,
            },
        ]

        password = 'FredsPass2026!'
        for w in workers:
            user, created = User.objects.get_or_create(username=w['username'])
            user.first_name = w['first_name']
            user.last_name = w['last_name']
            user.role = w['role']
            user.email = w['email']
            user.phone = w['phone']
            user.is_staff = w['is_staff']
            user.is_superuser = w['is_superuser']
            user.is_active = True
            user.active = True
            user.set_password(password)
            user.save()
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} worker '{user.username}' as {user.get_role_display()}"))

        self.stdout.write(self.style.SUCCESS("All worker accounts successfully configured with standard password."))
