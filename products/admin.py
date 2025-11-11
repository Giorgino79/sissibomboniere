from django.contrib import admin
from .models import Product, Category, ProductImages


class ProductImagesInline(admin.TabularInline):
    """Inline admin for product images"""
    model = ProductImages
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model"""
    list_display = ['title', 'category_image', 'product_count']
    search_fields = ['title']
    readonly_fields = ['cid', 'category_image']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model"""
    list_display = [
        'title', 
        'product_image', 
        'category', 
        'price', 
        'stock_count',
        'product_status',
        'featured',
        'date'
    ]
    list_filter = [
        'product_status', 
        'category', 
        'featured', 
        'in_stock',
        'digital',
        'date'
    ]
    search_fields = ['title', 'description', 'tags__name']
    readonly_fields = ['pid', 'sku', 'product_image', 'date', 'updated']
    list_editable = ['featured', 'product_status']
    inlines = [ProductImagesInline]
    
    fieldsets = (
        ('Informazioni Base', {
            'fields': ('pid', 'sku', 'title', 'category', 'user')
        }),
        ('Descrizione', {
            'fields': ('description', 'tags')
        }),
        ('Prezzi e Magazzino', {
            'fields': ('price', 'old_price', 'stock_count', 'weight')
        }),
        ('Media', {
            'fields': ('image', 'product_image')
        }),
        ('Stato e Opzioni', {
            'fields': ('product_status', 'status', 'in_stock', 'featured', 'digital')
        }),
        ('Date', {
            'fields': ('date', 'updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    """Admin interface for ProductImages model"""
    list_display = ['product', 'images', 'date']
    list_filter = ['date']
    search_fields = ['product__title']