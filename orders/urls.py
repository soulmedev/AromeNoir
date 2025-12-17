from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('payment/<int:order_id>/', views.payment_process, name='payment_process'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('history/', views.order_history, name='order_history'),
    path('success/', views.order_success, name='order_success'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]