"""
Admin configuration for core e-commerce models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem, Order, OrderItem, Payment, Wishlist, Review


class CartItemInline(admin.TabularInline):
    """Inline admin for cart items."""
    model = CartItem
    extra = 0
    readonly_fields = ('get_total',)
    fields = ('product', 'quantity', 'price', 'get_total')
    
    def get_total(self, obj):
        return f"€{obj.get_total():.2f}"
    get_total.short_description = 'Totale'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for Cart model."""
    list_display = ('cart_id', 'user', 'get_total_items', 'get_total_display', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('cart_id', 'user__email', 'session_key')
    readonly_fields = ('cart_id', 'created_at', 'updated_at', 'get_total_items', 'get_subtotal', 'get_total')
    inlines = [CartItemInline]
    
    def get_total_display(self, obj):
        return f"€{obj.get_total():.2f}"
    get_total_display.short_description = 'Totale'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin for CartItem model."""
    list_display = ('cart', 'product', 'quantity', 'price', 'get_total_display', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('cart__cart_id', 'product__title')
    readonly_fields = ('created_at', 'updated_at', 'get_total')
    
    def get_total_display(self, obj):
        return f"€{obj.get_total():.2f}"
    get_total_display.short_description = 'Totale'


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = OrderItem
    extra = 0
    readonly_fields = ('get_total',)
    fields = ('product', 'product_title', 'product_sku', 'quantity', 'price', 'get_total')
    
    def get_total(self, obj):
        return f"€{obj.get_total():.2f}"
    get_total.short_description = 'Totale'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for Order model."""
    list_display = (
        'order_id', 
        'full_name', 
        'email', 
        'get_total_display', 
        'order_status_badge',
        'created_at'
    )
    list_filter = ('order_status', 'created_at', 'updated_at')
    search_fields = ('order_id', 'email', 'full_name', 'phone')
    readonly_fields = (
        'order_id', 
        'created_at', 
        'updated_at', 
        'get_total_items',
        'subtotal',
        'shipping_cost',
        'tax',
        'total'
    )
    fieldsets = (
        ('Informazioni Ordine', {
            'fields': ('order_id', 'user', 'order_status', 'order_notes')
        }),
        ('Informazioni Cliente', {
            'fields': ('email', 'full_name', 'phone')
        }),
        ('Indirizzo di Spedizione', {
            'fields': (
                'shipping_address',
                'shipping_city',
                'shipping_state',
                'shipping_postal_code',
                'shipping_country'
            )
        }),
        ('Indirizzo di Fatturazione', {
            'fields': (
                'billing_address',
                'billing_city',
                'billing_state',
                'billing_postal_code',
                'billing_country'
            ),
            'classes': ('collapse',)
        }),
        ('Totali', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'total')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [OrderItemInline]
    
    def get_total_display(self, obj):
        return f"€{obj.total:.2f}"
    get_total_display.short_description = 'Totale'
    
    def order_status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'shipped': '#007bff',
            'delivered': '#28a745',
            'cancelled': '#dc3545',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.order_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_order_status_display()
        )
    order_status_badge.short_description = 'Stato'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for OrderItem model."""
    list_display = ('order', 'product_title', 'product_sku', 'quantity', 'price', 'get_total_display')
    list_filter = ('order__created_at',)
    search_fields = ('order__order_id', 'product_title', 'product_sku')
    readonly_fields = ('get_total',)
    
    def get_total_display(self, obj):
        return f"€{obj.get_total():.2f}"
    get_total_display.short_description = 'Totale'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payment model."""
    list_display = (
        'payment_id',
        'order',
        'payment_method',
        'payment_status_badge',
        'amount_display',
        'created_at'
    )
    list_filter = ('payment_method', 'payment_status', 'created_at')
    search_fields = (
        'payment_id',
        'order__order_id',
        'transaction_id',
        'paypal_order_id',
        'stripe_payment_intent_id'
    )
    readonly_fields = (
        'payment_id',
        'created_at',
        'updated_at',
        'paid_at'
    )
    fieldsets = (
        ('Informazioni Pagamento', {
            'fields': ('payment_id', 'order', 'payment_method', 'payment_status', 'amount')
        }),
        ('ID Esterni', {
            'fields': ('transaction_id', 'paypal_order_id', 'stripe_payment_intent_id')
        }),
        ('Risposta Pagamento', {
            'fields': ('payment_response',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at', 'paid_at')
        }),
    )
    
    def amount_display(self, obj):
        return f"€{obj.amount:.2f}"
    amount_display.short_description = 'Importo'
    
    def payment_status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.payment_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Stato'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin for Wishlist model."""
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'product__title')
    readonly_fields = ('created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin for Review model."""
    list_display = (
        'user',
        'product',
        'rating_stars',
        'title',
        'is_approved',
        'created_at'
    )
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('user__email', 'product__title', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_approved',)
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html('<span style="font-size: 16px;">{}</span>', stars)
    rating_stars.short_description = 'Valutazione'