"""
Django admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Address, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('Profile Information')
    extra = 0


class AddressInline(admin.TabularInline):
    """Inline admin for Address."""
    model = Address
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""
    
    inlines = (UserProfileInline, AddressInline)
    
    # List display
    list_display = (
        'email',
        'first_name', 
        'last_name',
        'is_active',
        'is_staff',
        'created_at',
        'newsletter_subscription'
    )
    
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'newsletter_subscription',
        'created_at',
        'last_login'
    )
    
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    
    # Fieldsets for change form
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal Info'), {
            'fields': (
                'first_name',
                'last_name', 
                'phone',
                'date_of_birth',
                'bio',
                'avatar'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff', 
                'is_superuser',
                'groups',
                'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        (_('Preferences'), {
            'fields': ('newsletter_subscription',),
        }),
    )
    
    # Fieldsets for add form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'first_name',
                'last_name',
                'password1',
                'password2'
            ),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    # Custom methods
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('profile')


@admin.register(Address) 
class AddressAdmin(admin.ModelAdmin):
    """Admin for Address model."""
    
    list_display = (
        'user',
        'full_name',
        'city',
        'country',
        'address_type',
        'is_default',
        'is_active'
    )
    
    list_filter = (
        'address_type',
        'is_default',
        'is_active',
        'country',
        'created_at'
    )
    
    search_fields = (
        'user__email',
        'full_name',
        'street_address',
        'city',
        'postal_code'
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'address_type')
        }),
        (_('Address Information'), {
            'fields': (
                'full_name',
                'company',
                'street_address',
                'apartment',
                'city',
                'state_province', 
                'postal_code',
                'country',
                'phone'
            )
        }),
        (_('Settings'), {
            'fields': ('is_default', 'is_active')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model."""
    
    list_display = (
        'user',
        'preferred_language',
        'email_notifications',
        'total_orders',
        'total_spent'
    )
    
    list_filter = (
        'preferred_language',
        'email_notifications', 
        'sms_notifications',
        'gender',
        'created_at'
    )
    
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    
    readonly_fields = ('total_orders', 'total_spent', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        (_('Personal Information'), {
            'fields': ('gender',)
        }),
        (_('Preferences'), {
            'fields': (
                'preferred_language',
                'favorite_categories',
                'email_notifications',
                'sms_notifications'
            )
        }),
        (_('Statistics'), {
            'fields': ('total_orders', 'total_spent'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
