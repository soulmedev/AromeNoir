from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart

try:
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
except ImportError:
    stripe = None

def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total_price = cart.get_total_price()
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Очищаємо кошик перед збереженням сесії
            cart.clear()
            
            # Зберігаємо order_id після очищення кошика
            request.session['order_id'] = order.id
            
            # Переконуємося, що сесія не містить Decimal об'єктів
            # Очищаємо кошик з сесії, якщо він там залишився
            from django.conf import settings
            if settings.CART_SESSION_ID in request.session:
                del request.session[settings.CART_SESSION_ID]
            
            request.session.modified = True
            
            # Перенаправляємо на сторінку оплати Stripe
            return redirect(reverse('orders:payment_process', args=[order.id]))
            
    else:
        form = OrderCreateForm()
        if request.user.is_authenticated:
            form = OrderCreateForm(initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            })
    
    return render(request, 'orders/order_create.html', {
        'cart': cart,
        'form': form
    })

def order_success(request):
    order_id = request.session.get('order_id')
    if order_id:
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'orders/order_success.html', {'order': order})
    return redirect('products:home')

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.user != request.user:
        return redirect('orders:order_history')
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/order_history.html', {'orders': orders})

def payment_process(request, order_id):
    if stripe is None:
        return render(request, 'orders/payment.html', {
            'order': get_object_or_404(Order, id=order_id),
            'error': 'Stripe не встановлено. Будь ласка, встановіть: pip install stripe',
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        })
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        try:
            # Створюємо Payment Intent в Stripe
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_price * 100),  # Конвертуємо в копійки
                currency='uah',
                metadata={
                    'order_id': order.id,
                    'customer_email': order.email,
                },
            )
            
            order.stripe_payment_intent_id = intent.id
            order.save()
            
            return render(request, 'orders/payment.html', {
                'order': order,
                'client_secret': intent.client_secret,
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            })
        except stripe.error.StripeError as e:
            return render(request, 'orders/payment.html', {
                'order': order,
                'error': str(e),
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            })
    else:
        try:
            # Перевіряємо, чи вже є payment intent
            if order.stripe_payment_intent_id:
                intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent_id)
            else:
                # Створюємо новий Payment Intent
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total_price * 100),
                    currency='uah',
                    metadata={
                        'order_id': order.id,
                        'customer_email': order.email,
                    },
                )
                order.stripe_payment_intent_id = intent.id
                order.save()
            
            return render(request, 'orders/payment.html', {
                'order': order,
                'client_secret': intent.client_secret,
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            })
        except stripe.error.StripeError as e:
            return render(request, 'orders/payment.html', {
                'order': order,
                'error': str(e),
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            })

def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Перевіряємо статус оплати через Stripe
    if order.stripe_payment_intent_id and stripe:
        try:
            intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent_id)
            if intent.status == 'succeeded' and not order.paid:
                order.paid = True
                order.status = 'processing'
                order.save()
                
                # Очищаємо кошик
                cart = Cart(request)
                cart.clear()
        except Exception:
            pass
    
    return render(request, 'orders/order_success.html', {'order': order})

@csrf_exempt
@require_POST
def stripe_webhook(request):
    if stripe is None:
        return HttpResponse(status=500)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Обробка подій
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata'].get('order_id')
        
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.paid = True
                order.status = 'processing'
                order.save()
                
                # Очищаємо кошик
                # (потрібно буде зберігати session_id в order для цього)
            except Order.DoesNotExist:
                pass
    
    return HttpResponse(status=200)