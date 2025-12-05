from django.urls import path
from . import views

app_name = "support"

urlpatterns = [
    path("delivery-payment/", views.delivery_payment, name="delivery_payment"),
    path("returns/", views.returns, name="returns"),
    path("faq/", views.faq, name="faq"),
    path("quality-guarantee/", views.quality_guarantee, name="quality_guarantee"),
    path("certificates/", views.certificates, name="certificates"),
]
