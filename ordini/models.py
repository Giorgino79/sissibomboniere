from django.db import models
from django.conf import settings
from core.models import Order, OrderItem
from products.models import Product


class DeliveryNote(models.Model):
    """
    Bolla di consegna collegata all'ordine.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_note')
    delivery_note_number = models.CharField(max_length=50, unique=True)

    # Date
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateField(null=True, blank=True)

    # Informazioni trasporto
    carrier = models.CharField(max_length=200, blank=True, help_text="Nome del corriere")
    tracking_number = models.CharField(max_length=200, blank=True, help_text="Numero tracciamento")

    # Numero colli
    packages_count = models.PositiveIntegerField(default=1, help_text="Numero di colli spediti")

    # Note
    notes = models.TextField(blank=True)

    # Generazione PDF
    pdf_file = models.FileField(upload_to='delivery_notes/%Y/%m/', null=True, blank=True)

    # Chi ha creato la bolla
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='delivery_notes_created')

    class Meta:
        verbose_name = "Bolla di Consegna"
        verbose_name_plural = "Bolle di Consegna"
        ordering = ['-created_at']

    def __str__(self):
        return f"Bolla {self.delivery_note_number} - Ordine {self.order.order_id}"

    def save(self, *args, **kwargs):
        # Genera numero bolla se non esiste
        if not self.delivery_note_number:
            from django.utils import timezone
            year = timezone.now().year
            count = DeliveryNote.objects.filter(created_at__year=year).count() + 1
            self.delivery_note_number = f"BDC-{year}-{count:05d}"
        super().save(*args, **kwargs)


class StockMovement(models.Model):
    """
    Traccia i movimenti di magazzino legati agli ordini.
    """
    MOVEMENT_TYPES = [
        ('out', 'Uscita (Vendita)'),
        ('in', 'Entrata (Reso/Annullamento)'),
        ('adjustment', 'Rettifica'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='stock_movements')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, null=True, blank=True, related_name='stock_movements')

    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(help_text="Quantità movimentata (positivo o negativo)")

    # Stock prima e dopo
    stock_before = models.IntegerField(help_text="Stock prima del movimento")
    stock_after = models.IntegerField(help_text="Stock dopo il movimento")

    # Info movimento
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='stock_movements_created')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Movimento Magazzino"
        verbose_name_plural = "Movimenti Magazzino"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.title} ({self.quantity})"


class OrderProcessing(models.Model):
    """
    Traccia il processo di preparazione dell'ordine.
    """
    STATUS_CHOICES = [
        ('to_prepare', 'Da Preparare'),
        ('preparing', 'In Preparazione'),
        ('ready', 'Pronto per la Spedizione'),
        ('shipped', 'Spedito'),
        ('delivered', 'Consegnato'),
        ('cancelled', 'Annullato'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='processing')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to_prepare')

    # Date tracking
    started_at = models.DateTimeField(null=True, blank=True, help_text="Quando è iniziata la preparazione")
    ready_at = models.DateTimeField(null=True, blank=True, help_text="Quando è pronto per la spedizione")
    shipped_at = models.DateTimeField(null=True, blank=True, help_text="Quando è stato spedito")
    delivered_at = models.DateTimeField(null=True, blank=True, help_text="Quando è stato consegnato")

    # Verifica articoli
    items_verified = models.BooleanField(default=False, help_text="Articoli verificati in magazzino")

    # Staff assignments
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders',
        help_text="Operatore assegnato alla preparazione"
    )

    # Note interne
    internal_notes = models.TextField(blank=True, help_text="Note interne per lo staff")

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Processo Ordine"
        verbose_name_plural = "Processi Ordini"
        ordering = ['-created_at']

    def __str__(self):
        return f"Processo {self.order.order_id} - {self.get_status_display()}"


class OrderNote(models.Model):
    """
    Note dell'amministratore sull'ordine.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='admin_notes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.TextField()
    is_important = models.BooleanField(default=False, help_text="Contrassegna come importante")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nota Ordine"
        verbose_name_plural = "Note Ordini"
        ordering = ['-created_at']

    def __str__(self):
        return f"Nota su {self.order.order_id} da {self.user.username}"


class OrderItemVerification(models.Model):
    """
    Verifica degli articoli dell'ordine (checklist di preparazione).
    """
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='verification')
    verified = models.BooleanField(default=False)
    verified_quantity = models.PositiveIntegerField(default=0, help_text="Quantità effettivamente verificata")
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Problemi o note sulla verifica")

    class Meta:
        verbose_name = "Verifica Articolo"
        verbose_name_plural = "Verifiche Articoli"

    def __str__(self):
        return f"Verifica {self.order_item.product_title} - {'✓' if self.verified else '✗'}"
