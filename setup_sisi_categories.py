#!/usr/bin/env python
"""
Script per configurare categorie specifiche per Sisi Bomboniere
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append('/home/giorgio/Scrivania/sisi')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomprj.settings')
django.setup()

from core.models import Category
from django.contrib.auth import get_user_model

User = get_user_model()

def setup_bomboniere_categories():
    """
    Crea le categorie specifiche per bomboniere
    """
    print("🎀 Configurando categorie Sisi Bomboniere...")
    
    # Categorie bomboniere specifiche
    bomboniere_categories = [
        {
            'title': 'MATRIMONIO',
            'description': 'Bomboniere eleganti per il giorno più bello'
        },
        {
            'title': 'BATTESIMO', 
            'description': 'Dolci ricordi per il sacramento del battesimo'
        },
        {
            'title': 'CRESIMA',
            'description': 'Bomboniere raffinate per la confermazione'
        },
        {
            'title': 'PRIMA COMUNIONE',
            'description': 'Ricordi speciali per la prima comunione'
        },
        {
            'title': 'LAUREA',
            'description': 'Celebra il traguardo con stile'
        },
        {
            'title': 'COMPLEANNO',
            'description': 'Bomboniere per feste di compleanno'
        },
        {
            'title': 'ANNIVERSARIO',
            'description': 'Ricordi per celebrare gli anniversari'
        },
        {
            'title': 'NASCITA',
            'description': 'Benvenuto al mondo con dolcezza'
        },
        {
            'title': 'BOMBONIERE RELIGIOSE',
            'description': 'Articoli per occasioni religiose'
        },
        {
            'title': 'BOMBONIERE SOLIDALI',
            'description': 'Bomboniere che fanno del bene'
        }
    ]
    
    created_count = 0
    
    for cat_data in bomboniere_categories:
        category, created = Category.objects.get_or_create(
            title=cat_data['title'],
            defaults={
                'image': 'category.jpg'  # Immagine di default, sostituire successivamente
            }
        )
        
        if created:
            created_count += 1
            print(f"  ✅ Categoria creata: {cat_data['title']}")
        else:
            print(f"  ℹ️  Categoria esistente: {cat_data['title']}")
    
    print(f"\n🎉 Configurazione completata!")
    print(f"📊 Categorie totali: {Category.objects.count()}")
    print(f"📈 Nuove categorie create: {created_count}")
    
    print(f"""
📋 PROSSIMI PASSI PER LE CATEGORIE:
1. Caricare immagini specifiche per ogni categoria in media/category/
2. Aggiornare le descrizioni delle categorie dall'admin
3. Aggiungere prodotti per ogni categoria
4. Configurare SEO per ogni categoria
5. Ottimizzare le immagini per il web

🎨 SUGGERIMENTI IMMAGINI:
- matrimonio.jpg: Anelli, fiori bianchi, eleganza
- battesimo.jpg: Colori pastello, angioletti
- cresima.jpg: Simboli religiosi, colori sobri  
- comunione.jpg: Calice, ostia, bianco e oro
- laurea.jpg: Tocco accademico, pergamena
""")

if __name__ == '__main__':
    setup_bomboniere_categories()