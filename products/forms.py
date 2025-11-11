from django import forms
from .models import Product, Category
from django_ckeditor_5.widgets import CKEditor5Widget


class ProductForm(forms.ModelForm):
    """Form for creating and editing products"""
    
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='extends'),
        required=False,
        label="Descrizione Completa"
    )
    
    class Meta:
        model = Product
        fields = [
            'title', 
            'description', 
            'category', 
            'price', 
            'old_price',
            'stock_count', 
            'weight',
            'image', 
            'tags', 
            'product_status',
            'featured',
            'in_stock',
            'digital'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Inserisci il nome del prodotto'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'old_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'stock_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Separa i tag con virgole'
            }),
            'product_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'in_stock': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'digital': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        labels = {
            'title': 'Titolo del Prodotto',
            'category': 'Categoria',
            'price': 'Prezzo di Vendita (€)',
            'old_price': 'Vecchio Prezzo (€)',
            'stock_count': 'Quantità in Magazzino',
            'weight': 'Peso (kg)',
            'image': 'Immagine Principale',
            'tags': 'Tags',
            'product_status': 'Stato del Prodotto',
            'featured': 'In Evidenza',
            'in_stock': 'Disponibile',
            'digital': 'Prodotto Digitale'
        }


class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories"""
    
    class Meta:
        model = Category
        fields = ['title', 'image']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Inserisci il nome della categoria'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        
        labels = {
            'title': 'Nome Categoria',
            'image': 'Immagine Categoria'
        }