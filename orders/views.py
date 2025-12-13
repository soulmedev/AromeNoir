from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            cart.clear()
            
            request.session['order_id'] = order.id
            
            return redirect(reverse('orders:order_success'))
            
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