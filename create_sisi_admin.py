#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/home/giorgio/Scrivania/sisi')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomprj.settings')
django.setup()

from django.contrib.auth import get_user_model
from userauths.models import Profile

User = get_user_model()

# Crea superuser per Sisi Bomboniere
admin_user, created = User.objects.get_or_create(
    email='admin@sisibomboniere.com',
    defaults={
        'username': 'sisi_admin',
        'is_superuser': True,
        'is_staff': True
    }
)

if created:
    admin_user.set_password('sisi123')
    admin_user.save()
    print("✅ Amministratore Sisi Bomboniere creato!")
else:
    print("ℹ️  Amministratore già esistente")

# Crea/aggiorna il profilo
profile, created = Profile.objects.get_or_create(
    user=admin_user,
    defaults={
        'full_name': 'Sisi Bomboniere Admin',
        'bio': 'Amministratore negozio Sisi Bomboniere - Specialisti in bomboniere per ogni occasione'
    }
)

print(f"""
🎀 SISI BOMBONIERE - CREDENZIALI ADMIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 Email: admin@sisibomboniere.com
🔐 Password: sisi123
👤 Nome: {profile.full_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")