"""
Views for core app.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from products.models import Category, Product
from .models import Cart, CartItem, Order, OrderItem, Payment, Wishlist, Review
from decimal import Decimal
import json


class HomeView(TemplateView):
    """Homepage view."""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Home'
        # Get main categories for homepage
        context['categories'] = Category.objects.all()[:4]
        # Get 4 random products for carousel
        context['featured_products'] = Product.objects.filter(
            status=True,
            in_stock=True,
            product_status='published'
        ).order_by('?')[:4]
        return context


class AboutView(TemplateView):
    """About page view."""
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Chi Siamo'
        return context


class ContactView(TemplateView):
    """Contact page view."""
    template_name = 'core/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Contatti'
        return context


# ============================================================================
# CART VIEWS
# ============================================================================

def get_or_create_cart(request):
    """
    Get or create cart for user or session.
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # For guest users, use session
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    return cart


def cart_view(request):
    """
    Display shopping cart.
    """
    cart = get_or_create_cart(request)
    
    context = {
        'page_title': 'Carrello',
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
    }
    
    return render(request, 'core/cart.html', context)


@require_POST
def add_to_cart(request, pid):
    """
    Add product to cart (AJAX).
    """
    try:
        product = get_object_or_404(Product, pid=pid)
        
        # Check if product is available
        if not product.in_stock or product.product_status != 'published':
            return JsonResponse({
                'success': False,
                'message': 'Prodotto non disponibile'
            }, status=400)
        
        # Get quantity from request
        quantity = int(request.POST.get('quantity', 1))
        
        # Check stock
        if quantity > product.stock_count:
            return JsonResponse({
                'success': False,
                'message': f'Disponibili solo {product.stock_count} unità'
            }, status=400)
        
        # Get or create cart
        cart = get_or_create_cart(request)
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'price': product.price, 'quantity': quantity}
        )
        
        if not created:
            # Update quantity if item already exists
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock_count:
                return JsonResponse({
                    'success': False,
                    'message': f'Disponibili solo {product.stock_count} unità'
                }, status=400)
            cart_item.quantity = new_quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Prodotto aggiunto al carrello',
            'cart_total_items': cart.get_total_items(),
            'cart_total': float(cart.get_total())
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_POST
def update_cart_item(request, item_id):
    """
    Update cart item quantity (AJAX).
    """
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            message = 'Prodotto rimosso dal carrello'
        else:
            # Check stock
            if quantity > cart_item.product.stock_count:
                return JsonResponse({
                    'success': False,
                    'message': f'Disponibili solo {cart_item.product.stock_count} unità'
                }, status=400)
            
            cart_item.quantity = quantity
            cart_item.save()
            message = 'Quantità aggiornata'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_total_items': cart.get_total_items(),
            'cart_subtotal': float(cart.get_subtotal()),
            'cart_shipping': float(cart.get_shipping_cost()),
            'cart_tax': float(cart.get_tax()),
            'cart_total': float(cart.get_total()),
            'item_total': float(cart_item.get_total()) if quantity > 0 else 0
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_POST
def remove_from_cart(request, item_id):
    """
    Remove item from cart (AJAX).
    """
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Prodotto rimosso dal carrello',
            'cart_total_items': cart.get_total_items(),
            'cart_subtotal': float(cart.get_subtotal()),
            'cart_shipping': float(cart.get_shipping_cost()),
            'cart_tax': float(cart.get_tax()),
            'cart_total': float(cart.get_total())
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


def clear_cart(request):
    """
    Clear all items from cart.
    """
    cart = get_or_create_cart(request)
    cart.clear()
    messages.success(request, 'Carrello svuotato')
    return redirect('core:cart')


# ============================================================================
# CHECKOUT VIEWS
# ============================================================================

def checkout_view(request):
    """
    Checkout page.
    """
    cart = get_or_create_cart(request)
    
    # Check if cart is empty
    if cart.get_total_items() == 0:
        messages.warning(request, 'Il carrello è vuoto')
        return redirect('core:cart')
    
    # Get user addresses if authenticated
    addresses = None
    if request.user.is_authenticated:
        addresses = request.user.addresses.filter(is_active=True)
    
    context = {
        'page_title': 'Checkout',
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
        'addresses': addresses,
    }
    
    return render(request, 'core/checkout.html', context)


def send_order_confirmation_emails(order, request):
    """
    Send order confirmation emails to customer and admin.
    """
    try:
        # Get site URL
        site_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash

        # Context for email templates
        context = {
            'order': order,
            'site_url': site_url,
            'contact_email': settings.CONTACT_EMAIL,
        }

        # === EMAIL TO CUSTOMER ===
        # Render HTML email
        html_content_customer = render_to_string('emails/order_confirmation_customer.html', context)

        # Create email message
        customer_email = EmailMultiAlternatives(
            subject=f'Conferma Ordine #{order.order_id} - Sisi Bomboniere',
            body=f'Grazie per il tuo ordine! Ordine #{order.order_id} ricevuto con successo.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        customer_email.attach_alternative(html_content_customer, "text/html")
        customer_email.send()

        # === EMAIL TO ADMIN ===
        # Render HTML email
        html_content_admin = render_to_string('emails/order_notification_admin.html', context)

        # Create email message
        admin_email = EmailMultiAlternatives(
            subject=f'🔔 Nuovo Ordine #{order.order_id} - {order.full_name}',
            body=f'Nuovo ordine ricevuto da {order.full_name}. Ordine #{order.order_id}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL],
        )
        admin_email.attach_alternative(html_content_admin, "text/html")
        admin_email.send()

        return True

    except Exception as e:
        # Log error but don't break checkout flow
        import traceback
        print("=" * 80)
        print(f"ERROR INVIO EMAIL ORDINE {order.order_id}")
        print(f"Errore: {str(e)}")
        print("Traceback completo:")
        traceback.print_exc()
        print("=" * 80)
        return False


@require_POST
def process_checkout(request):
    """
    Process checkout and create order from cart.
    """
    try:
        # 1. Get cart
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.error(request, 'Il carrello è vuoto.')
            return redirect('core:cart')

        # 2. Get form data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        shipping_address = request.POST.get('shipping_address')
        shipping_city = request.POST.get('shipping_city')
        shipping_state = request.POST.get('shipping_state')
        shipping_postal_code = request.POST.get('shipping_postal_code')
        payment_method = request.POST.get('payment_method')
        order_notes = request.POST.get('order_notes', '')

        # Billing address (optional, can be same as shipping)
        billing_address = request.POST.get('billing_address', '')
        billing_city = request.POST.get('billing_city', '')
        billing_state = request.POST.get('billing_state', '')
        billing_postal_code = request.POST.get('billing_postal_code', '')

        # 3. Validate required fields
        if not all([full_name, email, phone, shipping_address, shipping_city,
                   shipping_state, shipping_postal_code, payment_method]):
            messages.error(request, 'Compila tutti i campi obbligatori.')
            return redirect('core:checkout')

        # 4. Create Order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=email,
            full_name=full_name,
            phone=phone,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_state=shipping_state,
            shipping_postal_code=shipping_postal_code,
            billing_address=billing_address or shipping_address,
            billing_city=billing_city or shipping_city,
            billing_state=billing_state or shipping_state,
            billing_postal_code=billing_postal_code or shipping_postal_code,
            order_notes=order_notes,
        )

        # 5. Create OrderItems from CartItems
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_title=cart_item.product.title,
                product_sku=cart_item.product.sku,
                quantity=cart_item.quantity,
                price=cart_item.price,
            )

        # 6. Calculate order totals
        order.calculate_totals()

        # 7. Create Payment record
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.total,
            payment_status='pending',
        )

        # 8. Send confirmation emails
        email_sent = send_order_confirmation_emails(order, request)
        if not email_sent:
            # Don't fail checkout, just log it
            messages.warning(request, 'Ordine creato, ma c\'è stato un problema con l\'invio dell\'email di conferma.')

        # 9. Clear cart
        cart.clear()

        # 10. Redirect based on payment method
        if payment_method == 'paypal':
            # Redirect to PayPal checkout
            return redirect('core:paypal-checkout', order_id=order.order_id)
        elif payment_method == 'stripe':
            # Redirect to Stripe checkout
            return redirect('core:stripe-checkout', order_id=order.order_id)
        else:
            # Cash on delivery or bank transfer
            messages.success(request, f'Ordine {order.order_id} creato con successo! Controlla la tua email per la conferma.')
            return redirect('core:order-detail', order_id=order.order_id)

    except Exception as e:
        messages.error(request, f'Errore durante la creazione dell\'ordine: {str(e)}')
        return redirect('core:checkout')


# ============================================================================
# ORDER VIEWS
# ============================================================================

@login_required
def order_list_view(request):
    """
    Display user's orders.
    """
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    
    context = {
        'page_title': 'I Miei Ordini',
        'orders': orders,
    }
    
    return render(request, 'core/orders.html', context)


def order_detail_view(request, order_id):
    """
    Display order details.
    Accessible by both authenticated users and guests (via order_id).
    """
    # Get order
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        order_id=order_id
    )

    # Security: Check if user has access to this order
    if request.user.is_authenticated:
        # Authenticated users can only see their own orders
        if order.user != request.user and not request.user.is_staff:
            messages.error(request, 'Non hai i permessi per visualizzare questo ordine.')
            return redirect('core:home')
    # Guest users can see any order by ID (they need to know the exact order_id)
    # This is acceptable as order_id is a unique UUID

    context = {
        'page_title': f'Ordine {order.order_id}',
        'order': order,
    }

    return render(request, 'core/order_detail.html', context)


# ============================================================================
# WISHLIST VIEWS
# ============================================================================

@login_required
def wishlist_view(request):
    """
    Display user's wishlist.
    """
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'page_title': 'Lista Desideri',
        'wishlist_items': wishlist_items,
    }
    
    return render(request, 'core/wishlist.html', context)


@login_required
@require_POST
def add_to_wishlist(request, pid):
    """
    Add product to wishlist (AJAX).
    """
    try:
        product = get_object_or_404(Product, pid=pid)
        
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            return JsonResponse({
                'success': True,
                'message': 'Prodotto aggiunto alla lista desideri'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Prodotto già nella lista desideri'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_POST
def remove_from_wishlist(request, pid):
    """
    Remove product from wishlist (AJAX).
    """
    try:
        product = get_object_or_404(Product, pid=pid)
        Wishlist.objects.filter(user=request.user, product=product).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Prodotto rimosso dalla lista desideri'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

# ============================================================================
# PAYMENT INTEGRATION VIEWS
# ============================================================================

import paypalrestsdk
import stripe
from django.urls import reverse

# Configure PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

# Configure Stripe
if hasattr(settings, 'STRIPE_SECRET_KEY') and settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY != 'your-stripe-secret-key':
    stripe.api_key = settings.STRIPE_SECRET_KEY
    STRIPE_CONFIGURED = True
else:
    STRIPE_CONFIGURED = False


def paypal_checkout(request, order_id):
    """
    Create PayPal payment for order.
    """
    order = get_object_or_404(Order, order_id=order_id)
    
    # Create PayPal payment
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(
                reverse('core:paypal-execute', kwargs={'order_id': order.order_id})
            ),
            "cancel_url": request.build_absolute_uri(
                reverse('core:order-detail', kwargs={'order_id': order.order_id})
            )
        },
        "transactions": [{
            "item_list": {
                "items": [
                    {
                        "name": item.product_title,
                        "sku": item.product_sku or "N/A",
                        "price": str(item.price),
                        "currency": "EUR",
                        "quantity": item.quantity
                    }
                    for item in order.items.all()
                ]
            },
            "amount": {
                "total": str(order.total),
                "currency": "EUR",
                "details": {
                    "subtotal": str(order.subtotal),
                    "tax": str(order.tax),
                    "shipping": str(order.shipping_cost)
                }
            },
            "description": f"Ordine {order.order_id} - Sisi Bomboniere"
        }]
    })
    
    if payment.create():
        # Save PayPal payment ID
        order_payment = order.payment
        order_payment.transaction_id = payment.id
        order_payment.save()
        
        # Redirect to PayPal
        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)
    else:
        messages.error(request, f'Errore PayPal: {payment.error}')
        return redirect('core:order-detail', order_id=order.order_id)


def paypal_execute(request, order_id):
    """
    Execute PayPal payment after user approval.
    """
    order = get_object_or_404(Order, order_id=order_id)
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    payment = paypalrestsdk.Payment.find(payment_id)
    
    if payment.execute({"payer_id": payer_id}):
        # Update order payment status
        order_payment = order.payment
        order_payment.payment_status = 'completed'
        order_payment.transaction_id = payment_id
        order_payment.save()
        
        # Update order status
        order.order_status = 'processing'
        order.save()
        
        messages.success(request, f'Pagamento completato con successo! Ordine {order.order_id}')
        return redirect('core:order-detail', order_id=order.order_id)
    else:
        messages.error(request, f'Errore durante il pagamento: {payment.error}')
        return redirect('core:order-detail', order_id=order.order_id)


def stripe_checkout(request, order_id):
    """
    Create Stripe Checkout Session for order.
    """
    order = get_object_or_404(Order, order_id=order_id)

    # Check if Stripe is configured
    if not STRIPE_CONFIGURED:
        messages.warning(
            request,
            'Il pagamento con carta di credito non è al momento disponibile. '
            'Ti preghiamo di scegliere un metodo di pagamento alternativo (PayPal, Bonifico o Contrassegno). '
            'Ordine salvato con stato "In attesa di pagamento".'
        )
        # Update order status to pending payment
        order.order_status = 'pending'
        order.save()
        return redirect('core:order-detail', order_id=order.order_id)

    try:
        # Create line items for Stripe
        line_items = []
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': item.product_title,
                    },
                    'unit_amount': int(item.price * 100),  # Stripe uses cents
                },
                'quantity': item.quantity,
            })

        # Add shipping as a line item if > 0
        if order.shipping_cost > 0:
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Spedizione',
                    },
                    'unit_amount': int(order.shipping_cost * 100),
                },
                'quantity': 1,
            })

        # Create Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('core:stripe-success', kwargs={'order_id': order.order_id})
            ) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(
                reverse('core:order-detail', kwargs={'order_id': order.order_id})
            ),
            customer_email=order.email,
            metadata={
                'order_id': order.order_id,
            }
        )

        # Save session ID
        order_payment = order.payment
        order_payment.transaction_id = checkout_session.id
        order_payment.save()

        # Redirect to Stripe Checkout
        return redirect(checkout_session.url)

    except Exception as e:
        messages.error(request, f'Errore Stripe: {str(e)}')
        return redirect('core:order-detail', order_id=order.order_id)


def stripe_success(request, order_id):
    """
    Handle successful Stripe payment.
    """
    order = get_object_or_404(Order, order_id=order_id)
    session_id = request.GET.get('session_id')
    
    try:
        # Retrieve session
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            # Update order payment
            order_payment = order.payment
            order_payment.payment_status = 'completed'
            order_payment.transaction_id = session_id
            order_payment.save()
            
            # Update order status
            order.order_status = 'processing'
            order.save()
            
            messages.success(request, f'Pagamento completato con successo! Ordine {order.order_id}')
        else:
            messages.warning(request, 'Pagamento in attesa di conferma.')
        
        return redirect('core:order-detail', order_id=order.order_id)
        
    except Exception as e:
        messages.error(request, f'Errore: {str(e)}')
        return redirect('core:order-detail', order_id=order.order_id)


@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhooks for payment events.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session['metadata']['order_id']
        
        try:
            order = Order.objects.get(order_id=order_id)
            order_payment = order.payment
            order_payment.payment_status = 'completed'
            order_payment.save()
            
            order.order_status = 'processing'
            order.save()
        except Order.DoesNotExist:
            pass
    
    return JsonResponse({'status': 'success'})
