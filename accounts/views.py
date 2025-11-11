"""
Views for the accounts app.
Modern Django class-based views with proper authentication.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, UpdateView, DeleteView, 
    DetailView, ListView, TemplateView
)
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import User, Address, UserProfile
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm,
    UserProfileForm, UserPreferencesForm, AddressForm,
    PasswordChangeForm
)
from .decorators import profile_required, purchase_ready_required


class SignUpView(CreateView):
    """User registration view."""
    
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:profile')
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users."""
        if request.user.is_authenticated:
            return redirect('accounts:profile')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        
        # Log in the user after successful registration
        user = form.save()
        login(self.request, user)
        
        messages.success(
            self.request,
            'Benvenuto su Sisi Bomboniere! Il tuo account è stato creato con successo.'
        )

        return response

    def get_context_data(self, **kwargs):
        """Add extra context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crea Account'
        context['page_title'] = 'Registrati a Sisi Bomboniere'
        return context


def login_view(request):
    """Custom login view."""
    
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    form = CustomAuthenticationForm()
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Redirect to next URL or profile
                next_url = request.GET.get('next', reverse('accounts:profile'))
                
                messages.success(
                    request,
                    'Bentornato, {}!'.format(user.get_short_name())
                )
                
                return redirect(next_url)
            else:
                messages.error(request, 'Email o password non validi.')
        else:
            messages.error(request, 'Correggi gli errori qui sotto.')
    
    context = {
        'form': form,
        'title': 'Accedi',
        'page_title': 'Bentornato'
    }
    
    return render(request, 'accounts/login.html', context)


@login_required
def logout_view(request):
    """Custom logout view."""
    
    logout(request)
    messages.success(request, 'Sei uscito con successo.')
    return redirect('core:home')


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile dashboard view."""
    
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        """Add profile data to context."""
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        
        context.update({
            'user': user,
            'profile': user.profile,
            'addresses': user.addresses.filter(is_active=True)[:3],
            'title': 'Il Mio Profilo',
            'page_title': 'Pannello',
            # 'recent_orders': user.orders.all()[:5],  # Will be added when we create orders
        })
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile view."""
    
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        """Return the current user."""
        return self.request.user
    
    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(self.request, 'Il tuo profilo è stato aggiornato con successo.')
        return response
    
    def get_context_data(self, **kwargs):
        """Add extra context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifica Profilo'
        context['page_title'] = 'Aggiorna le Tue Informazioni'
        return context


class PreferencesView(LoginRequiredMixin, UpdateView):
    """Edit user preferences view."""
    
    model = UserProfile
    form_class = UserPreferencesForm
    template_name = 'accounts/preferences.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        """Return the current user's profile."""
        return self.request.user.profile
    
    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(self.request, 'Le tue preferenze sono state aggiornate con successo.')
        return response
    
    def get_context_data(self, **kwargs):
        """Add extra context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Preferenze'
        context['page_title'] = 'Preferenze Account'
        return context


class AddressListView(LoginRequiredMixin, ListView):
    """List user addresses."""
    
    model = Address
    template_name = 'accounts/address_list.html'
    context_object_name = 'addresses'
    paginate_by = 10
    
    def get_queryset(self):
        """Return user's addresses."""
        return self.request.user.addresses.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        """Add extra context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'I Miei Indirizzi'
        context['page_title'] = 'Gestisci Indirizzi'
        return context


class AddressCreateView(LoginRequiredMixin, CreateView):
    """Create new address."""
    
    model = Address
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:address-list')
    
    def form_valid(self, form):
        """Assign user to address."""
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Indirizzo aggiunto con successo.')
        return response
    
    def get_context_data(self, **kwargs):
        """Add extra context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Aggiungi Indirizzo'
        context['page_title'] = 'Nuovo Indirizzo'
        context['form_action'] = 'Aggiungi Indirizzo'
        return context


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing address."""
    
    model = Address
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:address-list')
    
    def get_queryset(self):
        """Return user's addresses only."""
        return self.request.user.addresses.filter(is_active=True)
    
    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(self.request, 'Indirizzo aggiornato con successo.')
        return response
    
    def get_context_data(self, **kwargs):
        """Add extra context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifica Indirizzo'
        context['page_title'] = 'Aggiorna Indirizzo'
        context['form_action'] = 'Aggiorna Indirizzo'
        return context


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    """Delete address (soft delete)."""
    
    model = Address
    template_name = 'accounts/address_confirm_delete.html'
    success_url = reverse_lazy('accounts:address-list')
    
    def get_queryset(self):
        """Return user's addresses only."""
        return self.request.user.addresses.filter(is_active=True)
    
    def delete(self, request, *args, **kwargs):
        """Soft delete the address."""
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        
        messages.success(request, 'Indirizzo eliminato con successo.')
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        """Add extra context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Elimina Indirizzo'
        context['page_title'] = 'Conferma Eliminazione'
        return context


@login_required
def password_change_view(request):
    """Change user password."""
    
    form = PasswordChangeForm(request.user)
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'La tua password è stata modificata con successo.')
            
            # Log the user back in with the new password
            user = authenticate(
                request,
                username=request.user.email,
                password=form.cleaned_data['new_password1']
            )
            if user:
                login(request, user)
            
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Correggi gli errori qui sotto.')
    
    context = {
        'form': form,
        'title': 'Cambia Password',
        'page_title': 'Aggiorna Password'
    }
    
    return render(request, 'accounts/password_change.html', context)


@login_required
def set_default_address(request, pk):
    """Set an address as default via AJAX."""
    
    if request.method == 'POST':
        address = get_object_or_404(
            Address,
            pk=pk,
            user=request.user,
            is_active=True
        )
        
        # Get address type to set as default
        address_type = address.address_type
        
        # Remove default from other addresses of same type
        Address.objects.filter(
            user=request.user,
            address_type=address_type,
            is_default=True
        ).update(is_default=False)
        
        # Set this address as default
        address.is_default = True
        address.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Indirizzo predefinito aggiornato con successo.'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Richiesta non valida.'
    })


@login_required
def account_deletion_view(request):
    """Account deletion view."""
    
    if request.method == 'POST':
        # Here you would implement account deletion logic
        # For now, we'll just deactivate the account
        
        user = request.user
        user.is_active = False
        user.save()
        
        logout(request)
        
        messages.success(
            request,
            'Il tuo account è stato disattivato. Ci dispiace vederti andare!'
        )
        
        return redirect('core:home')
    
    context = {
        'title': 'Elimina Account',
        'page_title': 'Eliminazione Account'
    }
    
    return render(request, 'accounts/account_deletion.html', context)


class ProfileCompletionView(LoginRequiredMixin, TemplateView):
    """Guide user through profile completion process."""
    
    template_name = 'accounts/profile_completion.html'
    
    def get_context_data(self, **kwargs):
        """Add profile completion data to context."""
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        missing_fields = user.get_missing_profile_fields()
        completion_percentage = user.get_profile_completion_percentage()
        
        # Determine next step
        next_step = None
        next_step_url = None
        
        if not user.first_name or not user.last_name:
            next_step = 'Completa le informazioni base'
            next_step_url = reverse('accounts:profile-edit')
        elif not user.phone:
            next_step = 'Aggiungi numero di telefono'
            next_step_url = reverse('accounts:profile-edit')
        elif not user.addresses.filter(is_active=True).exists():
            next_step = 'Aggiungi indirizzo di consegna'
            next_step_url = reverse('accounts:address-create')
        
        context.update({
            'missing_fields': missing_fields,
            'completion_percentage': completion_percentage,
            'is_profile_complete': user.is_profile_complete(),
            'is_purchase_ready': user.is_purchase_ready(),
            'next_step': next_step,
            'next_step_url': next_step_url,
            'title': 'Completa il Tuo Profilo',
            'page_title': 'Configurazione Profilo',
            # Additional context for template
            'profile_complete': user.first_name and user.last_name and user.phone,
            'has_address': user.addresses.filter(is_active=True).exists(),
            'preferences_set': user.profile.email_notifications or user.profile.sms_notifications,
            'newsletter_subscribed': user.newsletter_subscription,
        })
        
        return context


@login_required
def profile_completion_status(request):
    """AJAX endpoint for profile completion status."""
    
    user = request.user
    
    return JsonResponse({
        'completion_percentage': user.get_profile_completion_percentage(),
        'is_profile_complete': user.is_profile_complete(),
        'is_purchase_ready': user.is_purchase_ready(),
        'missing_fields': user.get_missing_profile_fields()
    })
