from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('products/', views.product_list, name='product_list'),
    path('stock-in/', views.stock_in, name='stock_in'),
    path('sales/create/', views.sale_create, name='sale_create'),
    path('sales/', views.sales_list, name='sales_list'),
    path('sale/', views.sale_create, name='sale_create'),
    path('analytics/', views.analytics, name='analytics'),
    path('products/add/', views.product_create, name='product_create'),
]
