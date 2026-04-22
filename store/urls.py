"""
Store URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search, name='search'),

    # Products
    path('products/', views.product_catalog, name='catalog'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),

    # Categories
    path('category/<slug:slug>/', views.category_page, name='category'),

    # Cart
    path('cart/', views.cart, name='cart'),
    path('cart/drawer/', views.cart_drawer, name='cart_drawer'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('order/<str:order_number>/confirmation/', views.order_confirmation, name='order_confirmation'),

    # Legal
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('cookies-policy/', views.cookies_policy, name='cookies_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('return-exchange/', views.return_exchange, name='return_exchange'),
]
