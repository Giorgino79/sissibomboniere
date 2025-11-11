from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category, ProductImages
from .forms import ProductForm, CategoryForm


@staff_member_required
def product_list(request):
    """
    Display list of all products with search and filter functionality
    Only accessible to staff members
    """
    products = Product.objects.all().select_related('category', 'user')
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category__cid=category_filter)
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        products = products.filter(product_status=status_filter)
    
    # Pagination
    paginator = Paginator(products, 20)  # Show 20 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'all_categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'page_title': 'Gestione Prodotti',
    }
    
    return render(request, 'products/product_list.html', context)


@staff_member_required
def product_add(request):
    """
    Add a new product
    Only accessible to staff members
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            form.save_m2m()  # Save tags
            messages.success(request, f'Prodotto "{product.title}" creato con successo!')
            return redirect('products:product-list')
        else:
            messages.error(request, 'Errore nella creazione del prodotto. Controlla i campi.')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'page_title': 'Aggiungi Nuovo Prodotto',
        'button_text': 'Crea Prodotto'
    }
    
    return render(request, 'products/product_form.html', context)


@staff_member_required
def product_edit(request, pid):
    """
    Edit an existing product
    Only accessible to staff members
    """
    product = get_object_or_404(Product, pid=pid)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Prodotto "{product.title}" aggiornato con successo!')
            return redirect('products:product-list')
        else:
            messages.error(request, 'Errore nell\'aggiornamento del prodotto. Controlla i campi.')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'page_title': f'Modifica Prodotto: {product.title}',
        'button_text': 'Aggiorna Prodotto'
    }
    
    return render(request, 'products/product_form.html', context)


@staff_member_required
def product_delete(request, pid):
    """
    Delete a product
    Only accessible to staff members
    """
    product = get_object_or_404(Product, pid=pid)
    
    if request.method == 'POST':
        product_title = product.title
        product.delete()
        messages.success(request, f'Prodotto "{product_title}" eliminato con successo!')
        return redirect('products:product-list')
    
    context = {
        'product': product,
        'page_title': 'Elimina Prodotto'
    }
    
    return render(request, 'products/product_confirm_delete.html', context)


@staff_member_required
def category_list(request):
    """
    Display list of all categories
    Only accessible to staff members
    """
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        categories = categories.filter(title__icontains=search_query)
    
    context = {
        'categories': categories,
        'search_query': search_query,
        'page_title': 'Gestione Categorie',
    }
    
    return render(request, 'products/category_list.html', context)


@staff_member_required
def category_add(request):
    """
    Add a new category
    Only accessible to staff members
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Categoria "{category.title}" creata con successo!')
            return redirect('products:category-list')
        else:
            messages.error(request, 'Errore nella creazione della categoria. Controlla i campi.')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'page_title': 'Aggiungi Nuova Categoria',
        'button_text': 'Crea Categoria'
    }
    
    return render(request, 'products/category_form.html', context)


@staff_member_required
def category_edit(request, cid):
    """
    Edit an existing category
    Only accessible to staff members
    """
    category = get_object_or_404(Category, cid=cid)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Categoria "{category.title}" aggiornata con successo!')
            return redirect('products:category-list')
        else:
            messages.error(request, 'Errore nell\'aggiornamento della categoria. Controlla i campi.')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'page_title': f'Modifica Categoria: {category.title}',
        'button_text': 'Aggiorna Categoria'
    }
    
    return render(request, 'products/category_form.html', context)


@staff_member_required
def category_delete(request, cid):
    """
    Delete a category
    Only accessible to staff members
    """
    category = get_object_or_404(Category, cid=cid)
    
    if request.method == 'POST':
        category_title = category.title
        product_count = category.product_count()
        
        if product_count > 0:
            messages.warning(
                request, 
                f'Impossibile eliminare la categoria "{category_title}" perché contiene {product_count} prodotti.'
            )
            return redirect('products:category-list')
        
        category.delete()
        messages.success(request, f'Categoria "{category_title}" eliminata con successo!')
        return redirect('products:category-list')
    
    context = {
        'category': category,
        'product_count': category.product_count(),
        'page_title': 'Elimina Categoria'
    }
    
    return render(request, 'products/category_confirm_delete.html', context)


def category_products(request, cid):
    """
    Display products for a specific category
    Public view - accessible to all users
    Shows 4 products per page with discounted products first
    """
    category = get_object_or_404(Category, cid=cid)
    
    # Get all published products in this category
    products = Product.objects.filter(
        category=category,
        product_status='published',
        status=True,
        in_stock=True
    ).select_related('category', 'user')
    
    # Order by: discounted products first (old_price > 0), then by date
    # Using Case/When for conditional ordering
    from django.db.models import Case, When, Value, IntegerField
    products = products.annotate(
        has_discount=Case(
            When(old_price__gt=0, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    ).order_by('has_discount', '-date')
    
    # Pagination - 4 products per page
    paginator = Paginator(products, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
        'page_title': category.title,
    }
    
    return render(request, 'products/category_products.html', context)


def product_detail(request, pid):
    """
    Display product detail page
    Public view - accessible to all users
    """
    product = get_object_or_404(
        Product.objects.select_related('category', 'user'),
        pid=pid,
        product_status='published'
    )
    
    # Get additional product images
    product_images = ProductImages.objects.filter(product=product)
    
    # Get related products from same category
    related_products = Product.objects.filter(
        category=product.category,
        product_status='published'
    ).exclude(pid=pid)[:4]
    
    context = {
        'product': product,
        'product_images': product_images,
        'related_products': related_products,
        'page_title': product.title,
    }
    
    return render(request, 'products/product_detail.html', context)


def catalog_view(request):
    """
    Display all products catalog
    Public view - accessible to all users
    """
    # Get all published products
    products = Product.objects.filter(
        product_status='published',
        status=True,
        in_stock=True
    ).select_related('category', 'user')
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category__cid=category_filter)
    
    # Order by: discounted products first, then by date
    from django.db.models import Case, When, Value, IntegerField
    products = products.annotate(
        has_discount=Case(
            When(old_price__gt=0, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    ).order_by('has_discount', '-date')
    
    # Pagination - 12 products per page
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for filter
    categories = Category.objects.all()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'category_filter': category_filter,
        'page_title': 'Catalogo Prodotti',
    }
    
    return render(request, 'products/catalog.html', context)


def search_view(request):
    """
    Search products
    Public view - accessible to all users
    """
    search_query = request.GET.get('q', '')
    products = Product.objects.none()
    
    if search_query:
        products = Product.objects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__name__icontains=search_query),
            product_status='published',
            status=True,
            in_stock=True
        ).select_related('category', 'user').distinct()
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'search_query': search_query,
        'page_title': f'Risultati per "{search_query}"' if search_query else 'Ricerca',
    }
    
    return render(request, 'products/search_results.html', context)