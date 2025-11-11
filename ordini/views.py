from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.views.decorators.http import require_POST

from core.models import Order, OrderItem
from products.models import Product
from .models import (
    DeliveryNote, StockMovement, OrderProcessing,
    OrderNote, OrderItemVerification
)
from .forms import (
    OrderProcessingForm, OrderStatusUpdateForm, DeliveryNoteForm,
    OrderNoteForm, OrderItemVerificationForm, OrderFilterForm
)


def is_staff(user):
    """Check if user is staff/admin"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff)
def dashboard(request):
    """
    Dashboard principale per la gestione ordini.
    """
    # Statistiche ordini
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(order_status='pending').count()
    processing_orders = Order.objects.filter(order_status='processing').count()
    shipped_orders = Order.objects.filter(order_status='shipped').count()

    # Ordini da preparare
    orders_to_prepare = OrderProcessing.objects.filter(
        status='to_prepare'
    ).select_related('order').order_by('-created_at')[:10]

    # Ordini in preparazione
    orders_in_progress = OrderProcessing.objects.filter(
        status='preparing'
    ).select_related('order', 'assigned_to').order_by('-updated_at')[:10]

    # Ultimi movimenti di magazzino
    recent_stock_movements = StockMovement.objects.select_related(
        'product', 'order'
    ).order_by('-created_at')[:10]

    # Note importanti
    important_notes = OrderNote.objects.filter(
        is_important=True
    ).select_related('order', 'user').order_by('-created_at')[:5]

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'orders_to_prepare': orders_to_prepare,
        'orders_in_progress': orders_in_progress,
        'recent_stock_movements': recent_stock_movements,
        'important_notes': important_notes,
    }

    return render(request, 'ordini/dashboard.html', context)


@login_required
@user_passes_test(is_staff)
def order_list(request):
    """
    Lista completa degli ordini con filtri.
    """
    orders = Order.objects.all().order_by('-created_at')

    # Form filtri
    filter_form = OrderFilterForm(request.GET or None)

    if filter_form.is_valid():
        # Filtro ricerca
        if filter_form.cleaned_data.get('search'):
            search = filter_form.cleaned_data['search']
            orders = orders.filter(
                Q(order_id__icontains=search) |
                Q(full_name__icontains=search) |
                Q(email__icontains=search)
            )

        # Filtro stato
        if filter_form.cleaned_data.get('status'):
            orders = orders.filter(order_status=filter_form.cleaned_data['status'])

        # Filtro metodo pagamento
        if filter_form.cleaned_data.get('payment_method'):
            orders = orders.filter(payment__payment_method=filter_form.cleaned_data['payment_method'])

        # Filtro data da
        if filter_form.cleaned_data.get('date_from'):
            orders = orders.filter(created_at__gte=filter_form.cleaned_data['date_from'])

        # Filtro data a
        if filter_form.cleaned_data.get('date_to'):
            orders = orders.filter(created_at__lte=filter_form.cleaned_data['date_to'])

    context = {
        'orders': orders,
        'filter_form': filter_form,
    }

    return render(request, 'ordini/order_list.html', context)


@login_required
@user_passes_test(is_staff)
def order_detail(request, order_id):
    """
    Dettaglio ordine con tutte le informazioni e azioni disponibili.
    """
    order = get_object_or_404(Order, order_id=order_id)

    # Ottieni o crea OrderProcessing
    processing, created = OrderProcessing.objects.get_or_create(order=order)

    # Forms
    processing_form = OrderProcessingForm(instance=processing)
    status_form = OrderStatusUpdateForm(instance=order)
    note_form = OrderNoteForm()

    # Verifica articoli con forms
    order_items_with_verification = []
    for item in order.items.all():
        verification, created = OrderItemVerification.objects.get_or_create(
            order_item=item,
            defaults={'verified_quantity': 0}
        )
        verification_form = OrderItemVerificationForm(instance=verification)
        order_items_with_verification.append({
            'item': item,
            'verification': verification,
            'form': verification_form,
        })

    # Note ordine
    notes = order.admin_notes.all().order_by('-created_at')

    # Bolla di consegna se esiste
    delivery_note = None
    try:
        delivery_note = order.delivery_note
    except DeliveryNote.DoesNotExist:
        pass

    # Movimenti di magazzino collegati
    stock_movements = order.stock_movements.all().order_by('-created_at')

    context = {
        'order': order,
        'processing': processing,
        'processing_form': processing_form,
        'status_form': status_form,
        'note_form': note_form,
        'order_items_with_verification': order_items_with_verification,
        'notes': notes,
        'delivery_note': delivery_note,
        'stock_movements': stock_movements,
    }

    return render(request, 'ordini/order_detail.html', context)


@login_required
@user_passes_test(is_staff)
@require_POST
def process_order(request, order_id):
    """
    Avvia o aggiorna il processo di preparazione ordine.
    """
    order = get_object_or_404(Order, order_id=order_id)
    processing, created = OrderProcessing.objects.get_or_create(order=order)

    action = request.POST.get('action')

    if action == 'start':
        processing.status = 'preparing'
        processing.started_at = timezone.now()
        processing.assigned_to = request.user
        processing.save()
        messages.success(request, f'Preparazione ordine {order.order_id} avviata.')

    elif action == 'mark_ready':
        processing.status = 'ready'
        processing.ready_at = timezone.now()
        processing.save()
        order.order_status = 'processing'
        order.save()
        messages.success(request, f'Ordine {order.order_id} pronto per la spedizione.')

    elif action == 'mark_shipped':
        processing.status = 'shipped'
        processing.shipped_at = timezone.now()
        processing.save()
        order.order_status = 'shipped'
        order.save()
        messages.success(request, f'Ordine {order.order_id} segnato come spedito.')

    elif action == 'mark_delivered':
        processing.status = 'delivered'
        processing.delivered_at = timezone.now()
        processing.save()
        order.order_status = 'completed'
        order.save()
        messages.success(request, f'Ordine {order.order_id} completato.')

    return redirect('ordini:order-detail', order_id=order.order_id)


@login_required
@user_passes_test(is_staff)
@require_POST
def update_order_status(request, order_id):
    """
    Aggiorna lo stato dell'ordine.
    """
    order = get_object_or_404(Order, order_id=order_id)
    form = OrderStatusUpdateForm(request.POST, instance=order)

    if form.is_valid():
        form.save()
        messages.success(request, f'Stato ordine {order.order_id} aggiornato a {order.get_order_status_display()}.')
    else:
        messages.error(request, 'Errore nell\'aggiornamento dello stato.')

    return redirect('ordini:order-detail', order_id=order.order_id)


@login_required
@user_passes_test(is_staff)
@require_POST
def verify_order_item(request, item_id):
    """
    Verifica un articolo dell'ordine.
    """
    order_item = get_object_or_404(OrderItem, id=item_id)
    verification, created = OrderItemVerification.objects.get_or_create(
        order_item=order_item
    )

    form = OrderItemVerificationForm(request.POST, instance=verification)

    if form.is_valid():
        verification = form.save(commit=False)
        verification.verified_by = request.user
        verification.verified_at = timezone.now()
        verification.save()

        # Se tutti gli articoli sono verificati, aggiorna OrderProcessing
        order = order_item.order
        all_items_verified = all(
            OrderItemVerification.objects.filter(order_item=item).first().verified
            for item in order.items.all()
        )

        if all_items_verified:
            processing, _ = OrderProcessing.objects.get_or_create(order=order)
            processing.items_verified = True
            processing.save()

        # Crea movimento di magazzino se verificato
        if verification.verified and verification.verified_quantity > 0:
            product = order_item.product
            if product:
                stock_before = product.stock_quantity
                product.stock_quantity -= verification.verified_quantity
                product.save()

                StockMovement.objects.create(
                    product=product,
                    order=order,
                    order_item=order_item,
                    movement_type='out',
                    quantity=-verification.verified_quantity,
                    stock_before=stock_before,
                    stock_after=product.stock_quantity,
                    created_by=request.user,
                    notes=f"Verifica ordine {order.order_id}"
                )

        messages.success(request, f'Articolo "{order_item.product_title}" verificato e magazzino aggiornato.')
    else:
        messages.error(request, 'Errore nella verifica dell\'articolo.')

    return redirect('ordini:order-detail', order_id=order_item.order.order_id)


@login_required
@user_passes_test(is_staff)
def create_delivery_note(request, order_id):
    """
    Crea una bolla di consegna per l'ordine.
    """
    order = get_object_or_404(Order, order_id=order_id)

    # Controlla se esiste già
    try:
        delivery_note = order.delivery_note
        messages.warning(request, 'Bolla di consegna già esistente per questo ordine.')
        return redirect('ordini:view-delivery-note', note_id=delivery_note.id)
    except DeliveryNote.DoesNotExist:
        pass

    if request.method == 'POST':
        form = DeliveryNoteForm(request.POST)
        if form.is_valid():
            delivery_note = form.save(commit=False)
            delivery_note.order = order
            delivery_note.created_by = request.user
            delivery_note.save()

            messages.success(request, f'Bolla di consegna {delivery_note.delivery_note_number} creata con successo.')
            return redirect('ordini:view-delivery-note', note_id=delivery_note.id)
    else:
        form = DeliveryNoteForm()

    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'ordini/create_delivery_note.html', context)


@login_required
@user_passes_test(is_staff)
def view_delivery_note(request, note_id):
    """
    Visualizza bolla di consegna.
    """
    delivery_note = get_object_or_404(DeliveryNote, id=note_id)

    context = {
        'delivery_note': delivery_note,
        'order': delivery_note.order,
    }

    return render(request, 'ordini/view_delivery_note.html', context)


@login_required
@user_passes_test(is_staff)
def generate_delivery_note_pdf(request, note_id):
    """
    Genera PDF della bolla di consegna.
    TODO: Implementare generazione PDF con reportlab o weasyprint
    """
    delivery_note = get_object_or_404(DeliveryNote, id=note_id)

    # Per ora restituiamo un messaggio
    messages.info(request, 'Funzionalità generazione PDF in fase di implementazione.')
    return redirect('ordini:view-delivery-note', note_id=note_id)


@login_required
@user_passes_test(is_staff)
@require_POST
def add_order_note(request, order_id):
    """
    Aggiungi una nota all'ordine.
    """
    order = get_object_or_404(Order, order_id=order_id)
    form = OrderNoteForm(request.POST)

    if form.is_valid():
        note = form.save(commit=False)
        note.order = order
        note.user = request.user
        note.save()
        messages.success(request, 'Nota aggiunta all\'ordine con successo.')
    else:
        messages.error(request, 'Errore nell\'aggiunta della nota.')

    return redirect('ordini:order-detail', order_id=order.order_id)


@login_required
@user_passes_test(is_staff)
def stock_movements(request):
    """
    Visualizza tutti i movimenti di magazzino.
    """
    movements = StockMovement.objects.all().select_related(
        'product', 'order', 'created_by'
    ).order_by('-created_at')

    # Filtri
    movement_type = request.GET.get('type')
    product_search = request.GET.get('product')

    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    if product_search:
        movements = movements.filter(
            Q(product__title__icontains=product_search) |
            Q(product__sku__icontains=product_search)
        )

    context = {
        'movements': movements,
        'movement_type': movement_type,
        'product_search': product_search,
    }

    return render(request, 'ordini/stock_movements.html', context)
