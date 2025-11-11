"""
URL configuration for accounts app.
"""

from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile URLs
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile-edit'),
    path('preferences/', views.PreferencesView.as_view(), name='preferences'),
    path('password/change/', views.password_change_view, name='password-change'),
    
    # Address URLs
    path('addresses/', views.AddressListView.as_view(), name='address-list'),
    path('addresses/create/', views.AddressCreateView.as_view(), name='address-create'),
    path('addresses/<int:pk>/edit/', views.AddressUpdateView.as_view(), name='address-edit'),
    path('addresses/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address-delete'),
    path('addresses/<int:pk>/set-default/', views.set_default_address, name='address-set-default'),
    
    # Profile completion
    path('profile/completion/', views.ProfileCompletionView.as_view(), name='profile-completion'),
    path('api/profile/status/', views.profile_completion_status, name='profile-status-api'),
    
    # Account management
    path('delete/', views.account_deletion_view, name='account-delete'),
]