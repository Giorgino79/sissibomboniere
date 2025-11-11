"""
User models for Sisi Bomboniere e-commerce platform.
Modern Django 5.0 implementation with custom User model.
"""

from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os


class UserManager(BaseUserManager):
    """Custom manager for User model."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model with email as the primary identifier.
    Extends Django's AbstractUser with additional fields for e-commerce.
    """
    
    objects = UserManager()
    
    # Email as username
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. Enter a valid email address.')
    )
    
    # Optional username field (not required)
    username = models.CharField(
        _('username'),
        max_length=150,
        blank=True,
        null=True,
        help_text=_('Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    )
    
    # Personal information
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    
    # Profile information
    bio = models.TextField(_('bio'), max_length=500, blank=True)
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        help_text=_('Upload a profile picture')
    )
    
    # Preferences
    newsletter_subscription = models.BooleanField(
        _('newsletter subscription'),
        default=True,
        help_text=_('Receive our newsletter with latest offers')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    # Authentication settings
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        """Return string representation of user."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def get_full_name(self):
        """Return the full name for the user."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]
    
    def get_initials(self):
        """Return user initials for avatar placeholder."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[0].upper()
        else:
            return self.email[0].upper()
    
    def get_absolute_url(self):
        """Return the absolute URL for the user profile."""
        return reverse('accounts:profile', kwargs={'pk': self.pk})
    
    def is_profile_complete(self):
        """Check if user profile is complete for basic usage."""
        return all([
            self.first_name,
            self.last_name,
            self.email
        ])
    
    def is_purchase_ready(self):
        """Check if user profile is complete for making purchases."""
        basic_complete = self.is_profile_complete()
        has_phone = bool(self.phone)
        has_address = self.addresses.filter(is_active=True).exists()
        
        return basic_complete and has_phone and has_address
    
    def get_profile_completion_percentage(self):
        """Get profile completion percentage."""
        total_fields = 6
        completed_fields = 0
        
        # Basic required fields
        if self.first_name:
            completed_fields += 1
        if self.last_name:
            completed_fields += 1
        if self.email:
            completed_fields += 1
        
        # Purchase-ready fields
        if self.phone:
            completed_fields += 1
        if self.addresses.filter(is_active=True).exists():
            completed_fields += 1
        if self.avatar:
            completed_fields += 1
            
        return int((completed_fields / total_fields) * 100)
    
    def get_missing_profile_fields(self):
        """Get list of missing profile fields for purchase readiness."""
        missing = []
        
        if not self.first_name:
            missing.append('first_name')
        if not self.last_name:
            missing.append('last_name')
        if not self.phone:
            missing.append('phone')
        if not self.addresses.filter(is_active=True).exists():
            missing.append('address')
            
        return missing
    
    def save(self, *args, **kwargs):
        """Override save to resize avatar image."""
        super().save(*args, **kwargs)
        
        if self.avatar:
            self._resize_avatar()
    
    def _resize_avatar(self):
        """Resize avatar to 300x300 pixels."""
        try:
            img = Image.open(self.avatar.path)
            
            # Resize if larger than 300x300
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size, Image.Resampling.LANCZOS)
                img.save(self.avatar.path)
        except (OSError, IOError):
            # Handle cases where image cannot be processed
            pass


class Address(models.Model):
    """
    User address model for shipping and billing.
    """
    
    ADDRESS_TYPES = [
        ('billing', _('Billing Address')),
        ('shipping', _('Shipping Address')),
        ('both', _('Billing & Shipping')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_('user')
    )
    
    # Address type
    address_type = models.CharField(
        _('address type'),
        max_length=10,
        choices=ADDRESS_TYPES,
        default='both'
    )
    
    # Address fields
    full_name = models.CharField(_('full name'), max_length=100)
    company = models.CharField(_('company'), max_length=100, blank=True)
    street_address = models.CharField(_('street address'), max_length=200)
    apartment = models.CharField(_('apartment, suite, etc.'), max_length=50, blank=True)
    city = models.CharField(_('city'), max_length=100)
    state_province = models.CharField(_('state/province'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20)
    country = models.CharField(_('country'), max_length=100, default='Italia')
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    
    # Status
    is_default = models.BooleanField(_('is default'), default=False)
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
        ordering = ['-is_default', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'address_type'],
                condition=models.Q(is_default=True),
                name='unique_default_address_per_type'
            )
        ]
    
    def __str__(self):
        """Return string representation of address."""
        return f"{self.full_name} - {self.city}, {self.country}"
    
    def get_full_address(self):
        """Return formatted full address."""
        address_parts = [
            self.street_address,
            self.apartment,
            f"{self.city}, {self.state_province}",
            self.postal_code,
            self.country
        ]
        return '\n'.join(filter(None, address_parts))
    
    def save(self, *args, **kwargs):
        """Override save to handle default address logic."""
        if self.is_default:
            # Set all other addresses of the same type to not default
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    Extended user profile with additional e-commerce related fields.
    """
    
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
        ('N', _('Prefer not to say')),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('user')
    )
    
    # Additional personal information
    gender = models.CharField(
        _('gender'),
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )
    
    # Shopping preferences
    favorite_categories = models.JSONField(
        _('favorite categories'),
        default=list,
        blank=True,
        help_text=_('List of favorite product category IDs')
    )
    
    preferred_language = models.CharField(
        _('preferred language'),
        max_length=10,
        choices=[('it', 'Italiano'), ('en', 'English')],
        default='it'
    )
    
    # Marketing preferences
    email_notifications = models.BooleanField(
        _('email notifications'),
        default=True,
        help_text=_('Receive order updates and important notifications')
    )
    
    sms_notifications = models.BooleanField(
        _('SMS notifications'),
        default=False,
        help_text=_('Receive SMS for order updates')
    )
    
    # Statistics (read-only fields)
    total_orders = models.PositiveIntegerField(_('total orders'), default=0)
    total_spent = models.DecimalField(
        _('total spent'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        """Return string representation of profile."""
        return f"{self.user.email} - Profile"
    
    def update_stats(self):
        """Update user statistics from orders."""
        # This will be implemented when we add the Order model
        pass


# Signal to create profile when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)
