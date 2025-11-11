from django.urls import path
from . import views

app_name = 'ordini'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Gestione Ordini
    path('list/', views.order_list, name='order-list'),
    path('detail/<str:order_id>/', views.order_detail, name='order-detail'),
    path('process/<str:order_id>/', views.process_order, name='process-order'),
    path('update-status/<str:order_id>/', views.update_order_status, name='update-status'),

    # Verifica Articoli
    path('verify-item/<int:item_id>/', views.verify_order_item, name='verify-item'),

    # Bolla di Consegna
    path('create-delivery-note/<str:order_id>/', views.create_delivery_note, name='create-delivery-note'),
    path('delivery-note/<int:note_id>/', views.view_delivery_note, name='view-delivery-note'),
    path('delivery-note/<int:note_id>/pdf/', views.generate_delivery_note_pdf, name='delivery-note-pdf'),

    # Note
    path('add-note/<str:order_id>/', views.add_order_note, name='add-note'),

    # Magazzino
    path('stock-movements/', views.stock_movements, name='stock-movements'),
]
