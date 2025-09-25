#!/usr/bin/env python
"""
Script per ottimizzare la gestione magazzino per Sisi Bomboniere
"""
import os
import sys
import django
from django.db import transaction

# Setup Django
sys.path.append('/home/giorgio/Scrivania/sisi')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomprj.settings')
django.setup()

from core.models import Product, Category
from django.contrib.auth import get_user_model

User = get_user_model()

def create_inventory_management_system():
    """
    Crea sistema avanzato per gestione magazzino bomboniere
    """
    print("📦 Configurando sistema di gestione magazzino per Sisi Bomboniere...")
    
    # Definizioni livelli di stock
    stock_levels = {
        'CRITICAL': 5,      # Sotto questa soglia = CRITICO
        'LOW': 15,          # Sotto questa soglia = BASSO  
        'MEDIUM': 50,       # Sotto questa soglia = MEDIO
        'HIGH': 100         # Sopra questa soglia = ALTO
    }
    
    # Regole di business per bomboniere
    inventory_rules = {
        'MATRIMONIO': {
            'min_stock': 20,
            'reorder_point': 50,
            'max_stock': 200,
            'seasonal_multiplier': 1.5,  # Maggiore richiesta primavera/estate
            'lead_time_days': 7
        },
        'BATTESIMO': {
            'min_stock': 15,
            'reorder_point': 30,
            'max_stock': 100,
            'seasonal_multiplier': 1.2,
            'lead_time_days': 5
        },
        'CRESIMA': {
            'min_stock': 10,
            'reorder_point': 25,
            'max_stock': 80,
            'seasonal_multiplier': 1.3,
            'lead_time_days': 5
        },
        'PRIMA COMUNIONE': {
            'min_stock': 15,
            'reorder_point': 35,
            'max_stock': 120,
            'seasonal_multiplier': 2.0,  # Picco aprile-maggio
            'lead_time_days': 7
        },
        'LAUREA': {
            'min_stock': 8,
            'reorder_point': 20,
            'max_stock': 60,
            'seasonal_multiplier': 1.8,  # Picco luglio-ottobre
            'lead_time_days': 4
        }
    }
    
    print("📊 Livelli di stock configurati:")
    for level, quantity in stock_levels.items():
        print(f"  🔸 {level}: {quantity} pezzi")
    
    print("\n📋 Regole per categoria:")
    for category, rules in inventory_rules.items():
        print(f"  🎀 {category}:")
        print(f"     📦 Stock minimo: {rules['min_stock']}")
        print(f"     🔄 Punto riordino: {rules['reorder_point']}")
        print(f"     📈 Stock massimo: {rules['max_stock']}")
        print(f"     📅 Tempi consegna: {rules['lead_time_days']} giorni")
    
    return stock_levels, inventory_rules

def create_sample_inventory_data():
    """
    Crea prodotti di esempio per le categorie bomboniere
    """
    print("\n🎀 Creando prodotti di esempio per Sisi Bomboniere...")
    
    # Ottieni l'utente admin
    try:
        admin_user = User.objects.get(email='admin@sisibomboniere.com')
    except User.DoesNotExist:
        print("⚠️ Admin user non trovato, usando il primo superuser disponibile")
        admin_user = User.objects.filter(is_superuser=True).first()
    
    # Prodotti di esempio per ogni categoria
    sample_products = {
        'MATRIMONIO': [
            {
                'title': 'Bomboniera Cuore Cristallo',
                'price': 12.50,
                'old_price': 15.00,
                'stock_count': 45,
                'description': 'Elegante cuore in cristallo con base argentata, perfetto per matrimoni. Include confetti e sacchettino in organza.'
            },
            {
                'title': 'Portafoto Sposi Argento',
                'price': 8.90,
                'stock_count': 32,
                'description': 'Portafoto in argento con decorazioni floreali, ideale per matrimoni romantici.'
            }
        ],
        'BATTESIMO': [
            {
                'title': 'Angioletto Ceramica Azzurro',
                'price': 6.50,
                'stock_count': 28,
                'description': 'Tenero angioletto in ceramica azzurra per battesimi maschili. Include confetti azzurri.'
            },
            {
                'title': 'Angioletto Ceramica Rosa',
                'price': 6.50,
                'stock_count': 30,
                'description': 'Dolce angioletto in ceramica rosa per battesimi femminili. Include confetti rosa.'
            }
        ],
        'CRESIMA': [
            {
                'title': 'Croce Legno Ulivo',
                'price': 9.90,
                'stock_count': 22,
                'description': 'Croce artigianale in legno di ulivo benedetto, simbolo di fede per la cresima.'
            }
        ]
    }
    
    created_products = 0
    
    with transaction.atomic():
        for category_name, products in sample_products.items():
            try:
                category = Category.objects.get(title=category_name)
                
                for product_data in products:
                    product, created = Product.objects.get_or_create(
                        title=product_data['title'],
                        defaults={
                            'user': admin_user,
                            'category': category,
                            'price': product_data['price'],
                            'old_price': product_data.get('old_price', 0),
                            'stock_count': product_data['stock_count'],
                            'description': product_data['description'],
                            'product_status': 'published',
                            'in_stock': True,
                            'featured': True if 'Cuore Cristallo' in product_data['title'] else False
                        }
                    )
                    
                    if created:
                        created_products += 1
                        stock_status = get_stock_status(product_data['stock_count'])
                        print(f"  ✅ {product_data['title']} - Stock: {product_data['stock_count']} ({stock_status})")
                    
            except Category.DoesNotExist:
                print(f"  ⚠️ Categoria {category_name} non trovata")
    
    print(f"\n🎉 Prodotti creati: {created_products}")
    return created_products

def get_stock_status(stock_count):
    """
    Determina lo stato dello stock
    """
    if stock_count <= 5:
        return "🔴 CRITICO"
    elif stock_count <= 15:
        return "🟡 BASSO"
    elif stock_count <= 50:
        return "🟢 BUONO"
    else:
        return "🟦 ALTO"

def inventory_health_check():
    """
    Controlla lo stato generale dell'inventario
    """
    print("\n🔍 CONTROLLO STATO INVENTARIO")
    print("=" * 50)
    
    total_products = Product.objects.count()
    in_stock_products = Product.objects.filter(in_stock=True).count()
    out_of_stock = Product.objects.filter(stock_count=0).count()
    low_stock = Product.objects.filter(stock_count__lte=15, stock_count__gt=0).count()
    critical_stock = Product.objects.filter(stock_count__lte=5, stock_count__gt=0).count()
    
    print(f"📊 RIEPILOGO INVENTARIO:")
    print(f"  📦 Prodotti totali: {total_products}")
    print(f"  🟢 Disponibili: {in_stock_products}")
    print(f"  🔴 Esauriti: {out_of_stock}")
    print(f"  🟡 Stock basso (≤15): {low_stock}")
    print(f"  ⚠️ Stock critico (≤5): {critical_stock}")
    
    if critical_stock > 0:
        print(f"\n⚠️ ATTENZIONE: {critical_stock} prodotti in stato critico!")
        critical_products = Product.objects.filter(stock_count__lte=5, stock_count__gt=0)
        for product in critical_products:
            print(f"  🔴 {product.title}: {product.stock_count} pezzi rimasti")
    
    # Calcola valore inventario
    total_inventory_value = 0
    for product in Product.objects.filter(in_stock=True):
        total_inventory_value += float(product.price) * product.stock_count
    
    print(f"\n💰 Valore inventario totale: €{total_inventory_value:,.2f}")
    
    return {
        'total_products': total_products,
        'critical_stock': critical_stock,
        'low_stock': low_stock,
        'inventory_value': total_inventory_value
    }

def generate_reorder_report():
    """
    Genera report dei prodotti da riordinare
    """
    print("\n📋 REPORT RIORDINI")
    print("=" * 50)
    
    reorder_needed = []
    
    for category in Category.objects.all():
        category_products = Product.objects.filter(category=category, stock_count__lte=20)
        
        if category_products.exists():
            print(f"\n🎀 {category.title}:")
            for product in category_products:
                status = get_stock_status(product.stock_count)
                reorder_qty = 50 - product.stock_count  # Suggerimento riordino
                
                print(f"  {status} {product.title}")
                print(f"     Stock attuale: {product.stock_count}")
                print(f"     Suggerito riordino: {reorder_qty} pezzi")
                print(f"     Valore riordino: €{float(product.price) * reorder_qty:.2f}")
                
                reorder_needed.append({
                    'product': product.title,
                    'current_stock': product.stock_count,
                    'suggested_order': reorder_qty,
                    'value': float(product.price) * reorder_qty
                })
    
    total_reorder_value = sum(item['value'] for item in reorder_needed)
    print(f"\n💰 Valore totale riordini suggeriti: €{total_reorder_value:,.2f}")
    
    return reorder_needed

if __name__ == '__main__':
    print("🎀 SISI BOMBONIERE - SETUP GESTIONE MAGAZZINO")
    print("=" * 60)
    
    # Configura sistema
    stock_levels, inventory_rules = create_inventory_management_system()
    
    # Crea prodotti di esempio
    created_count = create_sample_inventory_data()
    
    # Controllo stato inventario
    health_data = inventory_health_check()
    
    # Report riordini
    reorder_data = generate_reorder_report()
    
    print(f"""
🎉 CONFIGURAZIONE MAGAZZINO COMPLETATA!

📊 RISULTATI:
• Prodotti di esempio creati: {created_count}
• Prodotti in stock critico: {health_data['critical_stock']}
• Prodotti con stock basso: {health_data['low_stock']}
• Valore inventario: €{health_data['inventory_value']:,.2f}

📋 PROSSIMI PASSI:
1. Configurare notifiche automatiche per stock basso
2. Implementare sistema di riordino automatico
3. Creare dashboard per monitoraggio inventario
4. Integrare con fornitori per ordini automatici
5. Configurare report periodici via email

💡 FUNZIONALITÀ CONSIGLIATE:
• Alert automatici per stock critico
• Previsioni stagionali (es. picchi matrimoni)
• Integrazione barcode/QR per tracciamento
• Report vendite per categoria
• Analisi trend e rotazione stock
""")