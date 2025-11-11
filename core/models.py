"""
Core models for e-commerce functionality.
Includes Cart, Order, OrderItem, and Payment models.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from shortuuid.django_fields import ShortUUIDField
from products.models import Product
from decimal import Decimal

User = get_user_model()


# Order Status Choices
ORDER_STATUS = (
    ('pending', _('In Attesa')),
    ('processing', _('In Elaborazione')),
    ('shipped', _('Spedito')),
    ('delivered', _('Consegnato')),
    ('cancelled', _('Annullato')),
    ('refunded', _('Rimborsato')),
)

# Payment Status Choices
PAYMENT_STATUS = (
    ('pending', _('In Attesa')),
    ('processing', _('In Elaborazione')),
    ('completed', _('Completato')),
    ('failed', _('Fallito')),
    ('refunded', _('Rimborsato')),
)

# Payment Method Choices
PAYMENT_METHOD = (
    ('paypal', _('PayPal')),
    ('stripe', _('Carta di Credito/Debito')),
    ('bank_transfer', _('Bonifico Bancario')),
    ('cash_on_delivery', _('Contrassegno')),
)


class Cart(models.Model):
    """
    Shopping Cart Model.
    Stores cart items for both authenticated and guest users.
    """
    cart_id = ShortUUIDField(
        unique=True,
        length=10,
        max_length=20,
        prefix="cart",
        alphabet="abcdefgh12345"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name=_('Utente')
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name=_('Sessione')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Creato il'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Aggiornato il'))
    
    class Meta:
        verbose_name = _('Carrello')
        verbose_name_plural = _('Carrelli')
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.user:
            return f"Carrello di {self.user.email}"
        return f"Carrello Ospite {self.cart_id}"
    
    def get_total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    def get_subtotal(self):
        """Calculate cart subtotal (sum of all items)."""
        return sum(item.get_total() for item in self.items.all())
    
    def get_shipping_cost(self):
        """Calculate shipping cost based on subtotal."""
        subtotal = self.get_subtotal()
        if subtotal >= 50:  # Free shipping over €50
            return Decimal('0.00')
        return Decimal('5.00')  # Standard shipping €5
    
    def get_tax(self):
        """Calculate tax (IVA 22%)."""
        subtotal = self.get_subtotal()
        return (subtotal * Decimal('0.22')).quantize(Decimal('0.01'))
    
    def get_total(self):
        """Calculate cart total including shipping and tax."""
        subtotal = self.get_subtotal()
        shipping = self.get_shipping_cost()
        tax = self.get_tax()
        return subtotal + shipping + tax
    
    def clear(self):
        """Remove all items from cart."""
        self.items.all().delete()


class CartItem(models.Model):
    """
    Cart Item Model.
    Represents individual products in a cart.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Carrello')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_('Prodotto')
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantità'))
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Prezzo')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Aggiunto il'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Aggiornato il'))
    
    class Meta:
        verbose_name = _('Articolo Carrello')
        verbose_name_plural = _('Articoli Carrello')
        ordering = ['-created_at']
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity}x {self.product.title}"
    
    def get_total(self):
        """Calculate total price for this item."""
        return self.price * self.quantity
    
    def save(self, *args, **kwargs):
        """Override save to store current product price."""
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)


class Order(models.Model):
    """
    Order Model.
    Represents a customer order.
    """
    order_id = ShortUUIDField(
        unique=True,
        length=10,
        max_length=20,
        prefix="ORD",
        alphabet="ABCDEFGH12345"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('Utente')
    )
    
    # Customer Information
    email = models.EmailField(verbose_name=_('Email'))
    full_name = models.CharField(max_length=100, verbose_name=_('Nome Completo'))
    phone = models.CharField(max_length=20, verbose_name=_('Telefono'))
    
    # Shipping Address
    shipping_address = models.TextField(verbose_name=_('Indirizzo di Spedizione'))
    shipping_city = models.CharField(max_length=100, verbose_name=_('Città'))
    shipping_state = models.CharField(max_length=100, verbose_name=_('Provincia'))
    shipping_postal_code = models.CharField(max_length=20, verbose_name=_('CAP'))
    shipping_country = models.CharField(max_length=100, default='Italia', verbose_name=_('Paese'))
    
    # Billing Address (optional, can be same as shipping)
    billing_address = models.TextField(blank=True, verbose_name=_('Indirizzo di Fatturazione'))
    billing_city = models.CharField(max_length=100, blank=True, verbose_name=_('Città'))
    billing_state = models.CharField(max_length=100, blank=True, verbose_name=_('Provincia'))
    billing_postal_code = models.CharField(max_length=20, blank=True, verbose_name=_('CAP'))
    billing_country = models.CharField(max_length=100, blank=True, verbose_name=_('Paese'))
    
    # Order Totals
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Subtotale')
    )
    shipping_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Costo Spedizione')
    )
    tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name=_('IVA')
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Totale')
    )
    
    # Order Status
    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default='pending',
        verbose_name=_('Stato Ordine')
    )
    
    # Notes
    order_notes = models.TextField(blank=True, verbose_name=_('Note Ordine'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Creato il'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Aggiornato il'))
    
    class Meta:
        verbose_name = _('Ordine')
        verbose_name_plural = _('Ordini')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Ordine {self.order_id} - {self.full_name}"
    
    def get_total_items(self):
        """Get total number of items in order."""
        return sum(item.quantity for item in self.items.all())
    
    def calculate_totals(self):
        """Calculate and update order totals."""
        self.subtotal = sum(item.get_total() for item in self.items.all())
        
        # Calculate shipping
        if self.subtotal >= 50:
            self.shipping_cost = Decimal('0.00')
        else:
            self.shipping_cost = Decimal('5.00')
        
        # Calculate tax (IVA 22%)
        self.tax = (self.subtotal * Decimal('0.22')).quantize(Decimal('0.01'))
        
        # Calculate total
        self.total = self.subtotal + self.shipping_cost + self.tax
        
        self.save()


class OrderItem(models.Model):
    """
    Order Item Model.
    Represents individual products in an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Ordine')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Prodotto')
    )
    product_title = models.CharField(max_length=200, verbose_name=_('Nome Prodotto'))
    product_sku = models.CharField(max_length=20, verbose_name=_('SKU'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantità'))
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Prezzo Unitario')
    )
    
    class Meta:
        verbose_name = _('Articolo Ordine')
        verbose_name_plural = _('Articoli Ordine')
    
    def __str__(self):
        return f"{self.quantity}x {self.product_title}"
    
    def get_total(self):
        """Calculate total price for this item."""
        return self.price * self.quantity


class Payment(models.Model):
    """
    Payment Model.
    Tracks payment information for orders.
    """
    payment_id = ShortUUIDField(
        unique=True,
        length=10,
        max_length=20,
        prefix="PAY",
        alphabet="ABCDEFGH12345"
    )
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name=_('Ordine')
    )
    
    # Payment Details
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD,
        verbose_name=_('Metodo di Pagamento')
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending',
        verbose_name=_('Stato Pagamento')
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Importo')
    )
    
    # External Payment Gateway IDs
    transaction_id = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('ID Transazione')
    )
    paypal_order_id = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('PayPal Order ID')
    )
    stripe_payment_intent_id = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Stripe Payment Intent ID')
    )
    
    # Payment Response (store full response as JSON)
    payment_response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Risposta Pagamento')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Creato il'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Aggiornato il'))
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Pagato il'))
    
    class Meta:
        verbose_name = _('Pagamento')
        verbose_name_plural = _('Pagamenti')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pagamento {self.payment_id} - {self.get_payment_method_display()}"


class Wishlist(models.Model):
    """
    Wishlist Model.
    Allows users to save products for later.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlists',
        verbose_name=_('Utente')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_('Prodotto')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Aggiunto il'))
    
    class Meta:
        verbose_name = _('Lista Desideri')
        verbose_name_plural = _('Liste Desideri')
        unique_together = ('user', 'product')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.title}"


class Review(models.Model):
    """
    Product Review Model.
    Allows users to review products.
    """
    RATING_CHOICES = (
        (1, '1 - Pessimo'),
        (2, '2 - Scarso'),
        (3, '3 - Sufficiente'),
        (4, '4 - Buono'),
        (5, '5 - Eccellente'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Utente')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Prodotto')
    )
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name=_('Valutazione'))
    title = models.CharField(max_length=200, verbose_name=_('Titolo'))
    comment = models.TextField(verbose_name=_('Commento'))
    
    # Moderation
    is_approved = models.BooleanField(default=False, verbose_name=_('Approvata'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Creata il'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Aggiornata il'))
    
    class Meta:
        verbose_name = _('Recensione')
        verbose_name_plural = _('Recensioni')
        unique_together = ('user', 'product')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.title} ({self.rating}★)"