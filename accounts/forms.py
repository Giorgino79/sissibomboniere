"""
Forms for the accounts app.
Modern Django forms with crispy-bootstrap5 styling.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, Row, Column, HTML, Submit
from crispy_forms.bootstrap import FormActions

from .models import User, Address, UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with email as username."""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nome',
        widget=forms.TextInput(attrs={
            'placeholder': 'Inserisci il tuo nome',
            'class': 'form-control'
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Cognome',
        widget=forms.TextInput(attrs={
            'placeholder': 'Inserisci il tuo cognome',
            'class': 'form-control'
        })
    )

    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Inserisci il tuo indirizzo email',
            'class': 'form-control'
        })
    )

    newsletter_subscription = forms.BooleanField(
        required=False,
        initial=True,
        label='Iscriviti alla nostra newsletter',
        help_text='Ricevi aggiornamenti su nuovi prodotti e offerte speciali'
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', 'newsletter_subscription')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize password fields
        self.fields['password1'].label = 'Password'
        self.fields['password1'].help_text = 'La password deve contenere almeno 8 caratteri'
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Inserisci la password',
            'class': 'form-control'
        })
        self.fields['password2'].label = 'Conferma Password'
        self.fields['password2'].help_text = 'Inserisci nuovamente la password per conferma'
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Conferma la password',
            'class': 'form-control'
        })

        # Setup crispy forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Field('email', css_class='mb-3'),
            Field('password1', css_class='mb-3'),
            Field('password2', css_class='mb-3'),
            Field('newsletter_subscription', css_class='mb-3'),
            Submit('submit', 'Crea Account', css_class='btn btn-primary w-100')
        )
    
    def save(self, commit=True):
        """Save user with email as username."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """Custom user change form for admin."""
    
    class Meta:
        model = User
        fields = '__all__'


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with email as username."""

    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Inserisci il tuo indirizzo email',
            'class': 'form-control'
        })
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Inserisci la tua password',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Field('username', css_class='mb-3'),
            Field('password', css_class='mb-3'),
            Submit('submit', 'Accedi', css_class='btn btn-primary w-100')
        )


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'date_of_birth', 
            'bio', 'avatar', 'newsletter_subscription'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Field('phone', css_class='mb-3'),
            Field('date_of_birth', css_class='mb-3'),
            Field('bio', css_class='mb-3'),
            Field('avatar', css_class='mb-3'),
            Field('newsletter_subscription', css_class='mb-3'),
            Submit('submit', _('Update Profile'), css_class='btn btn-primary')
        )


class UserPreferencesForm(forms.ModelForm):
    """Form for editing user preferences."""
    
    class Meta:
        model = UserProfile
        fields = [
            'preferred_language', 'email_notifications', 
            'sms_notifications', 'gender'
        ]
        widgets = {
            'preferred_language': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            Field('preferred_language', css_class='mb-3'),
            Field('gender', css_class='mb-3'),
            Field('email_notifications', css_class='mb-3'),
            Field('sms_notifications', css_class='mb-3'),
            Submit('submit', _('Update Preferences'), css_class='btn btn-primary')
        )


class AddressForm(forms.ModelForm):
    """Form for creating/editing addresses."""
    
    class Meta:
        model = Address
        fields = [
            'address_type', 'full_name', 'company', 'street_address',
            'apartment', 'city', 'state_province', 'postal_code',
            'country', 'phone', 'is_default'
        ]
        widgets = {
            'address_type': forms.Select(attrs={'class': 'form-select'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'apartment': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state_province': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            Row(
                Column('address_type', css_class='form-group col-md-6 mb-3'),
                Column('is_default', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Field('full_name', css_class='mb-3'),
            Field('company', css_class='mb-3'),
            Field('street_address', css_class='mb-3'),
            Field('apartment', css_class='mb-3'),
            Row(
                Column('city', css_class='form-group col-md-6 mb-3'),
                Column('state_province', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('postal_code', css_class='form-group col-md-6 mb-3'),
                Column('country', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Field('phone', css_class='mb-3'),
            Submit('submit', _('Save Address'), css_class='btn btn-primary')
        )


class PasswordChangeForm(forms.Form):
    """Custom password change form."""
    
    old_password = forms.CharField(
        label=_('Current Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your current password')
        })
    )
    
    new_password1 = forms.CharField(
        label=_('New Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your new password')
        })
    )
    
    new_password2 = forms.CharField(
        label=_('Confirm New Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm your new password')
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            Field('old_password', css_class='mb-3'),
            Field('new_password1', css_class='mb-3'),
            Field('new_password2', css_class='mb-3'),
            Submit('submit', _('Change Password'), css_class='btn btn-primary')
        )
    
    def clean_old_password(self):
        """Validate old password."""
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_('Your old password was entered incorrectly.'))
        return old_password
    
    def clean_new_password2(self):
        """Validate new password confirmation."""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        
        return password2
    
    def save(self):
        """Save the new password."""
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user
