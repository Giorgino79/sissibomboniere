import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomprj.settings')
sys.path.append(os.path.dirname(__file__))
django.setup()

from core.models import *
from userauths.models import *

def clean_demo_data():
    print("🧹 Pulizia dati demo in corso...")
    
    # Contare i record prima della pulizia
    products_count = Product.objects.count()
    categories_count = Category.objects.count()
    vendors_count = Vendor.objects.count()
    orders_count = CartOrder.objects.count()
    
    print(f"Prima della pulizia:")
    print(f"- Prodotti: {products_count}")
    print(f"- Categorie: {categories_count}")
    print(f"- Vendor: {vendors_count}")
    print(f"- Ordini: {orders_count}")
    
    # Rimuovere tutti i dati demo
    Product.objects.all().delete()
    Category.objects.all().delete()
    Vendor.objects.all().delete()
    CartOrder.objects.all().delete()
    CartOrderProducts.objects.all().delete()
    ProductReview.objects.all().delete()
    wishlist_model.objects.all().delete()
    Address.objects.all().delete()
    Coupon.objects.all().delete()
    
    print("✅ Database pulito dai dati demo")
    print("Tutti i dati demo sono stati rimossi con successo!")

if __name__ == "__main__":
    clean_demo_data()