#!/usr/bin/env python
"""
Script per personalizzazione automatica cliente
Uso: python setup_client.py --client=[NOME_CLIENTE]
"""
import os
import sys
import django
import argparse
from pathlib import Path

# Setup Django
sys.path.append('/home/giorgio/Scrivania/vecchio hp/PROGRAMMI PYTHON/django-ecom')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomprj.settings')
django.setup()

from core.models import Category, Product
from django.contrib.auth import get_user_model

def setup_client_customization(client_name, client_data):
    """
    Personalizza l'e-commerce per un cliente specifico
    """
    print(f"🎯 Configurando e-commerce per: {client_name}")
    
    # 1. Setup categorie cliente
    print("📦 Configurando categorie...")
    for cat_name in client_data.get('categories', []):
        cat, created = Category.objects.get_or_create(
            title=cat_name,
            defaults={'image': 'category.jpg'}
        )
        if created:
            print(f"  ✅ Categoria creata: {cat_name}")
    
    # 2. Setup admin utente
    print("👤 Configurando utente admin...")
    User = get_user_model()
    admin_email = client_data.get('admin_email', f'admin@{client_name.lower()}.com')
    
    if not User.objects.filter(email=admin_email).exists():
        user = User.objects.create_superuser(
            email=admin_email,
            username=client_name.lower(),
            password='admin123'  # DA CAMBIARE!
        )
        print(f"  ✅ Admin creato: {admin_email}")
    
    # 3. Crea cartelle personalizzate
    print("📁 Creando struttura file personalizzata...")
    client_static_dir = Path(f'static/assets/imgs/{client_name.lower()}')
    client_static_dir.mkdir(parents=True, exist_ok=True)
    print(f"  ✅ Cartella creata: {client_static_dir}")
    
    # 4. Genera CSS personalizzato
    print("🎨 Generando CSS personalizzato...")
    colors = client_data.get('colors', {})
    css_content = f"""
/* CSS Personalizzato per {client_name} */
:root {{
    --client-primary: {colors.get('primary', '#3BB77E')};
    --client-secondary: {colors.get('secondary', '#FDC040')};
    --client-accent: {colors.get('accent', '#FF6B35')};
}}

.btn-primary, .bg-primary {{ 
    background-color: var(--client-primary) !important; 
    border-color: var(--client-primary) !important; 
}}

.text-brand, .navbar-brand {{ 
    color: var(--client-primary) !important; 
}}

.navbar {{
    background-color: var(--client-primary) !important;
}}
"""
    
    css_file = Path(f'static/assets/css/client-{client_name.lower()}.css')
    css_file.write_text(css_content)
    print(f"  ✅ CSS creato: {css_file}")
    
    print(f"🎉 Configurazione completata per {client_name}!")
    print(f"""
📋 PROSSIMI PASSI:
1. Caricare logo in: static/assets/imgs/{client_name.lower()}/logo.png
2. Caricare immagini prodotti
3. Aggiornare contenuti in templates/
4. Configurare metodi pagamento
5. Testare e deployare

👤 CREDENZIALI ADMIN:
Email: {admin_email}
Password: admin123 (DA CAMBIARE!)
""")

# Configurazioni clienti di esempio
CLIENTS_CONFIG = {
    'fashionboutique': {
        'categories': ['Abbigliamento Donna', 'Abbigliamento Uomo', 'Accessori', 'Scarpe'],
        'colors': {'primary': '#E91E63', 'secondary': '#9C27B0', 'accent': '#FF9800'},
        'admin_email': 'admin@fashionboutique.com'
    },
    'elettroshop': {
        'categories': ['Smartphone', 'Computer', 'TV & Audio', 'Gaming', 'Accessori'],
        'colors': {'primary': '#2196F3', 'secondary': '#607D8B', 'accent': '#FF5722'},
        'admin_email': 'admin@elettroshop.com'
    },
    'biomarket': {
        'categories': ['Frutta e Verdura', 'Latticini Bio', 'Cereali', 'Bevande', 'Cura Persona'],
        'colors': {'primary': '#4CAF50', 'secondary': '#8BC34A', 'accent': '#FFC107'},
        'admin_email': 'admin@biomarket.com'
    }
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup cliente e-commerce')
    parser.add_argument('--client', required=True, help='Nome cliente')
    args = parser.parse_args()
    
    client_name = args.client.lower()
    
    if client_name in CLIENTS_CONFIG:
        setup_client_customization(client_name, CLIENTS_CONFIG[client_name])
    else:
        print(f"⚠️  Cliente '{client_name}' non trovato nei config predefiniti.")
        print("💡 Clienti disponibili:", list(CLIENTS_CONFIG.keys()))
        print("💡 Usa: python setup_client.py --client=[NOME]")