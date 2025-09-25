from core.models import Product, Category
from django import forms
# from bootstrap_datepicker_plus import DatePickerInput



class AddProductForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Nome Prodotto", "class":"form-control"}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "Descrizione Prodotto", "class":"form-control"}))
    price = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': "Prezzo", "class":"form-control"}))
    old_price = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': "Prezzo Precedente (opzionale)", "class":"form-control"}), required=False)
    stock_count = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': "Quantità disponibile", "class":"form-control"}))
    weight = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': "Peso (kg)", "class":"form-control"}), required=False)
    tags = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Tag (separati da virgola)", "class":"form-control"}), required=False)
    image = forms.ImageField(widget=forms.FileInput(attrs={"class":"form-control"}))
    
    class Meta:
        model = Product
        fields = [ 
            'title',
            'image',
            'description',
            'price',
            'old_price',
            'stock_count',
            'weight',
            'tags',
            'digital',
            'category',
            'product_status'
        ]

        widgets = {
        # 'mdf': DateTimePickerInput
    }


class AddCategoryForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Nome Categoria", "class":"form-control"}))
    image = forms.ImageField(widget=forms.FileInput(attrs={"class":"form-control"}))

    class Meta:
        model = Category
        fields = [
            'title',
            'image',
        ]