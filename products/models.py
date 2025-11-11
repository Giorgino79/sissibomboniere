from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from django.contrib.auth import get_user_model
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone

User = get_user_model()

STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)


def user_directory_path(instance, filename):
    """Generate upload path for user files"""
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Category(models.Model):
    """Product Category Model"""
    cid = ShortUUIDField(
        unique=True, 
        length=10, 
        max_length=20,
        prefix="cat", 
        alphabet="abcdefgh12345"
    )
    title = models.CharField(
        max_length=100, 
        default="Categoria", 
        verbose_name="Nome"
    )
    image = models.ImageField(
        upload_to="category", 
        default="category.jpg", 
        verbose_name="Immagine"
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorie"
        ordering = ['title']

    def category_image(self):
        """Display category image in admin"""
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def product_count(self):
        """Count products in this category"""
        return Product.objects.filter(category=self).count()

    def __str__(self):
        return self.title


class Product(models.Model):
    """Product Model"""
    pid = ShortUUIDField(
        unique=True, 
        length=10,
        max_length=20, 
        alphabet="abcdefgh12345"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Creato da"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="products",
        verbose_name="Categoria"
    )
    title = models.CharField(
        max_length=100, 
        default="Prodotto", 
        verbose_name="Nome"
    )
    image = models.ImageField(
        upload_to=user_directory_path, 
        default="product.jpg", 
        verbose_name="Immagine"
    )
    description = CKEditor5Field(
        config_name='extends', 
        null=True, 
        blank=True, 
        verbose_name="Descrizione"
    )
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default="0.00", 
        verbose_name="Prezzo"
    )
    old_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default="0.00", 
        null=True, 
        blank=True, 
        verbose_name="Prezzo precedente"
    )
    stock_count = models.IntegerField(
        default=0, 
        verbose_name="Quantità disponibile"
    )
    weight = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Peso (kg)"
    )
    tags = TaggableManager(blank=True)
    
    product_status = models.CharField(
        choices=STATUS, 
        max_length=10, 
        default="in_review",
        verbose_name="Stato"
    )
    status = models.BooleanField(default=True, verbose_name="Attivo")
    in_stock = models.BooleanField(default=True, verbose_name="Disponibile")
    featured = models.BooleanField(default=False, verbose_name="In evidenza")
    digital = models.BooleanField(default=False, verbose_name="Prodotto digitale")
    
    sku = ShortUUIDField(
        unique=True, 
        length=4, 
        max_length=10,
        prefix="sku", 
        alphabet="1234567890"
    )
    ean = models.CharField(
        max_length=13,
        null=True,
        blank=True,
        unique=True,
        verbose_name="Codice EAN",
        help_text="Codice a barre europeo (13 cifre)"
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="Data creazione")
    updated = models.DateTimeField(null=True, blank=True, verbose_name="Ultima modifica")

    class Meta:
        verbose_name = "Prodotto"
        verbose_name_plural = "Prodotti"
        ordering = ['-date']

    def product_image(self):
        """Display product image in admin"""
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

    def get_percentage(self):
        """Calculate discount percentage"""
        if self.old_price and self.old_price > 0:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return round(discount, 2)
        return 0

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        if self.pk:
            self.updated = timezone.now()
        super().save(*args, **kwargs)


class ProductImages(models.Model):
    """Additional Product Images Model"""
    images = models.ImageField(
        upload_to="product-images", 
        default="product.jpg",
        verbose_name="Immagine"
    )
    product = models.ForeignKey(
        Product, 
        related_name="p_images", 
        on_delete=models.CASCADE,
        verbose_name="Prodotto"
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="Data caricamento")

    class Meta:
        verbose_name = "Immagine Prodotto"
        verbose_name_plural = "Immagini Prodotto"
        ordering = ['-date']

    def __str__(self):
        return f"Immagine per {self.product.title}"