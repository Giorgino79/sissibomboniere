from django.contrib import admin
from .models import DeliveryNote, StockMovement, OrderProcessing, OrderNote, OrderItemVerification


@admin.register(DeliveryNote)
class DeliveryNoteAdmin(admin.ModelAdmin):
    list_display = ['delivery_note_number', 'order', 'carrier', 'tracking_number', 'created_at', 'delivery_date']
    list_filter = ['created_at', 'delivery_date', 'carrier']
    search_fields = ['delivery_note_number', 'order__order_id', 'tracking_number']
    readonly_fields = ['delivery_note_number', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'stock_before', 'stock_after', 'order', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['product__title', 'product__sku', 'order__order_id']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(OrderProcessing)
class OrderProcessingAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'items_verified', 'assigned_to', 'started_at', 'shipped_at']
    list_filter = ['status', 'items_verified', 'assigned_to']
    search_fields = ['order__order_id', 'order__email', 'order__full_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(OrderNote)
class OrderNoteAdmin(admin.ModelAdmin):
    list_display = ['order', 'user', 'is_important', 'created_at', 'note_preview']
    list_filter = ['is_important', 'created_at', 'user']
    search_fields = ['order__order_id', 'note']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    def note_preview(self, obj):
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'Anteprima Nota'


@admin.register(OrderItemVerification)
class OrderItemVerificationAdmin(admin.ModelAdmin):
    list_display = ['order_item', 'verified', 'verified_quantity', 'verified_by', 'verified_at']
    list_filter = ['verified', 'verified_at']
    search_fields = ['order_item__product_title', 'order_item__order__order_id']
    readonly_fields = ['verified_at']
