from django import forms
from django.contrib.auth import get_user_model
from .models import (
    DeliveryNote, OrderProcessing, OrderNote,
    OrderItemVerification, StockMovement
)
from core.models import Order, ORDER_STATUS

User = get_user_model()


class OrderProcessingForm(forms.ModelForm):
    """
    Form per gestire il processo di preparazione ordine.
    """
    class Meta:
        model = OrderProcessing
        fields = [
            'status',
            'assigned_to',
            'items_verified',
            'internal_notes',
        ]
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select',
            }),
            'items_verified': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'internal_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Note interne per lo staff...',
            }),
        }
        labels = {
            'status': 'Stato Preparazione',
            'assigned_to': 'Assegnato a',
            'items_verified': 'Articoli Verificati',
            'internal_notes': 'Note Interne',
        }


class OrderStatusUpdateForm(forms.ModelForm):
    """
    Form semplice per aggiornare solo lo stato dell'ordine.
    """
    class Meta:
        model = Order
        fields = ['order_status']
        widgets = {
            'order_status': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'order_status': 'Stato Ordine',
        }


class DeliveryNoteForm(forms.ModelForm):
    """
    Form per creare/modificare una bolla di consegna.
    """
    class Meta:
        model = DeliveryNote
        fields = [
            'carrier',
            'tracking_number',
            'packages_count',
            'delivery_date',
            'notes',
        ]
        widgets = {
            'carrier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Es: BRT, GLS, Poste Italiane...',
            }),
            'tracking_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numero di tracciamento',
            }),
            'packages_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1,
            }),
            'delivery_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Note aggiuntive sulla spedizione...',
            }),
        }
        labels = {
            'carrier': 'Corriere',
            'tracking_number': 'Numero Tracciamento',
            'packages_count': 'Numero Colli',
            'delivery_date': 'Data Consegna Prevista',
            'notes': 'Note',
        }


class OrderNoteForm(forms.ModelForm):
    """
    Form per aggiungere note all'ordine.
    """
    class Meta:
        model = OrderNote
        fields = ['note', 'is_important']
        widgets = {
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Scrivi una nota sull\'ordine...',
                'required': True,
            }),
            'is_important': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'note': 'Nota',
            'is_important': 'Contrassegna come importante',
        }


class OrderItemVerificationForm(forms.ModelForm):
    """
    Form per verificare un singolo articolo dell'ordine.
    """
    class Meta:
        model = OrderItemVerification
        fields = [
            'verified',
            'verified_quantity',
            'notes',
        ]
        widgets = {
            'verified': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'verified_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Problemi o note sulla verifica...',
            }),
        }
        labels = {
            'verified': 'Verificato',
            'verified_quantity': 'Quantita Verificata',
            'notes': 'Note',
        }


class StockAdjustmentForm(forms.Form):
    """
    Form per rettifiche manuali di magazzino.
    """
    product = forms.CharField(
        widget=forms.HiddenInput()
    )

    adjustment_type = forms.ChoiceField(
        choices=[
            ('in', 'Entrata (Aggiungi)'),
            ('out', 'Uscita (Sottrai)'),
            ('adjustment', 'Rettifica'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Tipo Movimento'
    )

    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Quantit�',
        }),
        label='Quantit�'
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Motivo della rettifica...',
        }),
        label='Note'
    )


class OrderFilterForm(forms.Form):
    """
    Form per filtrare gli ordini nella lista.
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cerca per ID, nome, email...',
        }),
        label='Cerca'
    )

    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Tutti gli stati')] + list(ORDER_STATUS),
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Stato Ordine'
    )

    payment_method = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Tutti i metodi'),
            ('paypal', 'PayPal'),
            ('stripe', 'Carta di Credito'),
            ('bank_transfer', 'Bonifico Bancario'),
            ('cash_on_delivery', 'Contrassegno'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Metodo di Pagamento'
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label='Da Data'
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label='A Data'
    )


class BulkOrderActionForm(forms.Form):
    """
    Form per azioni in blocco sugli ordini.
    """
    action = forms.ChoiceField(
        choices=[
            ('', 'Seleziona azione...'),
            ('mark_processing', 'Segna come In Elaborazione'),
            ('mark_shipped', 'Segna come Spedito'),
            ('mark_completed', 'Segna come Completato'),
            ('assign_to_me', 'Assegna a Me'),
            ('export_csv', 'Esporta CSV'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Azione'
    )

    order_ids = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
