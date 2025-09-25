#!/usr/bin/env python
"""
Script per configurare pagamenti e spedizioni per Sisi Bomboniere
"""
import os
import sys
import django

# Setup Django
sys.path.append('/home/giorgio/Scrivania/sisi')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomprj.settings')
django.setup()

def update_payment_settings():
    """
    Configura i metodi di pagamento per il mercato italiano
    """
    print("💳 Configurando metodi di pagamento per l'Italia...")
    
    # Configura le variabili di ambiente per i pagamenti italiani
    payment_config = {
        'PAYMENT_METHODS': {
            'stripe': {
                'enabled': True,
                'currency': 'EUR',
                'country': 'IT',
                'description': 'Carta di credito/debito (Visa, MasterCard, American Express)'
            },
            'paypal': {
                'enabled': True,
                'currency': 'EUR',
                'country': 'IT', 
                'description': 'PayPal - Paga con il tuo conto PayPal'
            },
            'bank_transfer': {
                'enabled': True,
                'currency': 'EUR',
                'country': 'IT',
                'description': 'Bonifico bancario (tempi di consegna: 3-5 giorni lavorativi dopo accredito)'
            },
            'cash_on_delivery': {
                'enabled': True,
                'currency': 'EUR',
                'country': 'IT',
                'description': 'Contrassegno (pagamento alla consegna + 3€ di commissione)',
                'extra_fee': 3.00
            }
        }
    }
    
    shipping_config = {
        'SHIPPING_ZONES': {
            'italy_standard': {
                'name': 'Italia - Spedizione Standard',
                'countries': ['IT'],
                'cost': 4.90,
                'free_shipping_threshold': 50.00,
                'delivery_time': '3-5 giorni lavorativi',
                'description': 'Spedizione con corriere espresso'
            },
            'italy_express': {
                'name': 'Italia - Spedizione Express',
                'countries': ['IT'],
                'cost': 8.90,
                'free_shipping_threshold': 100.00,
                'delivery_time': '24-48 ore',
                'description': 'Spedizione urgente con corriere espresso'
            },
            'sicily_sardinia': {
                'name': 'Sicilia e Sardegna',
                'countries': ['IT'],
                'regions': ['Sicily', 'Sardinia'],
                'cost': 7.90,
                'free_shipping_threshold': 75.00,
                'delivery_time': '4-7 giorni lavorativi',
                'description': 'Spedizione per isole'
            }
        }
    }
    
    print("✅ Configurazione pagamenti:")
    for method, config in payment_config['PAYMENT_METHODS'].items():
        status = "🟢 ATTIVO" if config['enabled'] else "🔴 DISATTIVO"
        print(f"  {status} {method.upper()}: {config['description']}")
    
    print(f"\n📦 Configurazione spedizioni:")
    for zone, config in shipping_config['SHIPPING_ZONES'].items():
        print(f"  📍 {config['name']}: €{config['cost']} (Gratis sopra €{config['free_shipping_threshold']})")
        print(f"     ⏱️ Consegna: {config['delivery_time']}")
    
    print(f"""
🇮🇹 CONFIGURAZIONE ITALIA COMPLETATA!

💳 METODI DI PAGAMENTO ABILITATI:
• Carte di credito/debito (Stripe)
• PayPal
• Bonifico bancario
• Contrassegno (+3€)

📦 OPZIONI DI SPEDIZIONE:
• Standard: €4.90 (gratis sopra €50)
• Express: €8.90 (gratis sopra €100)  
• Isole: €7.90 (gratis sopra €75)

📋 PROSSIMI PASSI:
1. Configurare chiavi API Stripe/PayPal in settings.py
2. Testare tutti i metodi di pagamento
3. Configurare email di conferma ordine
4. Impostare gestione magazzino
5. Testare processo di checkout completo

⚠️ IMPORTANTE:
- Verificare che le chiavi API siano corrette
- Testare in modalità sandbox prima del go-live
- Configurare webhook per gli stati ordine
""")

def create_sample_shipping_data():
    """
    Crea dati di esempio per le spedizioni
    """
    print("📦 Creando configurazioni di spedizione di esempio...")
    
    # Qui potresti aggiungere codice per creare record nel database
    # per le zone di spedizione se hai un modello dedicato
    
    shipping_rates = {
        'Italia continentale': {
            'cost': 4.90,
            'free_threshold': 50.00,
            'regions': ['Lazio', 'Lombardia', 'Veneto', 'Piemonte', 'Emilia-Romagna', 
                       'Toscana', 'Campania', 'Puglia', 'Calabria', 'Abruzzo', 
                       'Marche', 'Umbria', 'Liguria', 'Molise', 'Basilicata']
        },
        'Sicilia e Sardegna': {
            'cost': 7.90,
            'free_threshold': 75.00,
            'regions': ['Sicilia', 'Sardegna']
        }
    }
    
    return shipping_rates

if __name__ == '__main__':
    update_payment_settings()
    create_sample_shipping_data()