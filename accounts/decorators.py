"""
Custom decorators for accounts app.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def profile_required(view_func):
    """
    Decorator to ensure user has a complete basic profile.
    Redirects to profile completion page if profile is incomplete.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if not request.user.is_profile_complete():
            messages.warning(
                request,
                _('Please complete your profile before continuing.')
            )
            return redirect('accounts:profile-edit')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def purchase_ready_required(view_func):
    """
    Decorator to ensure user profile is complete for purchases.
    Requires: first_name, last_name, phone, and at least one address.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if not request.user.is_purchase_ready():
            missing_fields = request.user.get_missing_profile_fields()
            
            if 'address' in missing_fields:
                messages.warning(
                    request,
                    _('Please add at least one delivery address before making a purchase.')
                )
                return redirect('accounts:address-create')
            
            if 'phone' in missing_fields:
                messages.warning(
                    request,
                    _('Please add your phone number before making a purchase.')
                )
                return redirect('accounts:profile-edit')
            
            messages.warning(
                request,
                _('Please complete your profile before making a purchase.')
            )
            return redirect('accounts:profile-completion')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def ajax_login_required(view_func):
    """
    Decorator for AJAX views that require authentication.
    Returns JSON response instead of redirect.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from django.http import JsonResponse
        
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'authentication_required',
                'message': str(_('Authentication required'))
            }, status=401)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper