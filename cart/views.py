from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from products.models import Product
from .cart import Cart
from .forms import CartAddProductForm

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart_info = {
                'total_items': len(cart),
                'total_price': float(cart.get_total_price()),
                'success': True,
                'message': 'Товар додано до кошика'
            }
            return JsonResponse(cart_info)
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Невалідна форма',
                'errors': form.errors
            }, status=400)
            
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart_info = {
                'total_items': len(cart),
                'total_price': float(cart.get_total_price()),
                'is_empty': len(cart) == 0,
                'success': True,
                'message': 'Товар видалено з кошика'
            }
            return JsonResponse(cart_info)
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Помилка: {str(e)}'
            }, status=400)
        
    return redirect('cart:cart_detail')

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=True
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart_info = {
                'total_items': len(cart),
                'total_price': float(cart.get_total_price()),
                'item_total': float(cart.get_item_price(product)),
                'success': True,
                'message': 'Кошик оновлено'
            }
            return JsonResponse(cart_info)
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Невалідна форма',
                'errors': form.errors
            }, status=400)
            
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    cart_items = []
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
        cart_items.append(item)
    return render(request, 'cart/cart_detail.html', {
        'cart': cart_items,
        'cart_obj': cart,
        'has_items': len(cart_items) > 0,
        'is_authenticated': request.user.is_authenticated
    })
