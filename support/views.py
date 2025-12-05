from django.shortcuts import render

def delivery_payment(request):
    return render(request, "support/delivery_payment.html")

def returns(request):
    return render(request, "support/returns.html")

def faq(request):
    return render(request, "support/faq.html")

def quality_guarantee(request):
    return render(request, "support/quality_guarantee.html")

def certificates(request):
    return render(request, "support/certificates.html")