from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    # authentication is handled in users app now
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('login-success/', views.login_success, name='login_success'),
    # Cart and orders
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    # Category
    path('dashboard/categories/', views.category_list_create, name='category_list_url'),
    path('dashboard/categories/edit/<int:pk>/', views.category_edit, name='category_edit_url'),
    path('dashboard/categories/delete/<int:pk>/', views.category_delete, name='category_delete_url'),

    # Brand
    path('dashboard/brands/', views.brand_list_create, name='brand_list_url'),
    path('dashboard/brands/edit/<int:pk>/', views.brand_edit, name='brand_edit_url'),
    path('dashboard/brands/delete/<int:pk>/', views.brand_delete, name='brand_delete_url'),

    # Product
    path('dashboard/products/', views.product_list, name='product_list_url'),
    path('dashboard/products/create/', views.product_create, name='product_create_url'),
    path('dashboard/products/edit/<int:pk>/', views.product_edit, name='product_edit_url'),
    path('dashboard/products/delete/<int:pk>/', views.product_delete, name='product_delete_url'),


]

