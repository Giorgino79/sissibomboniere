"""
URL configuration for core app.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Cart URLs
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<str:pid>/', views.add_to_cart, name='add-to-cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update-cart-item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('cart/clear/', views.clear_cart, name='clear-cart'),
    
    # Checkout URLs
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/process/', views.process_checkout, name='checkout-process'),

    # Order URLs
    path('orders/', views.order_list_view, name='orders'),
    path('orders/<str:order_id>/', views.order_detail_view, name='order-detail'),
    
    # Wishlist URLs
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<str:pid>/', views.add_to_wishlist, name='add-to-wishlist'),
    path('wishlist/remove/<str:pid>/', views.remove_from_wishlist, name='remove-from-wishlist'),

    # Payment URLs - PayPal
    path('payment/paypal/<str:order_id>/', views.paypal_checkout, name='paypal-checkout'),
    path('payment/paypal/execute/<str:order_id>/', views.paypal_execute, name='paypal-execute'),

    # Payment URLs - Stripe
    path('payment/stripe/<str:order_id>/', views.stripe_checkout, name='stripe-checkout'),
    path('payment/stripe/success/<str:order_id>/', views.stripe_success, name='stripe-success'),
    path('payment/stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),
]