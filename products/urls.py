from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Public URLs (must be first to avoid conflicts)
    path('catalog/', views.catalog_view, name='catalog'),
    path('search/', views.search_view, name='search'),
    path('category/<str:cid>/', views.category_products, name='category-products'),
    
    # Admin Product URLs
    path('', views.product_list, name='product-list'),
    path('add/', views.product_add, name='product-add'),
    path('edit/<str:pid>/', views.product_edit, name='product-edit'),
    path('delete/<str:pid>/', views.product_delete, name='product-delete'),
    
    # Category URLs (admin)
    path('categories/', views.category_list, name='category-list'),
    path('categories/add/', views.category_add, name='category-add'),
    path('categories/edit/<str:cid>/', views.category_edit, name='category-edit'),
    path('categories/delete/<str:cid>/', views.category_delete, name='category-delete'),
    
    # Product detail (must be last to avoid conflicts)
    path('<str:pid>/', views.product_detail, name='product-detail'),
]