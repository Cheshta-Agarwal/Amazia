from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.dashboard, name='dashboard_root'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
]
