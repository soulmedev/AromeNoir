from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from products.models import Product
from .cart import Cart
from .forms import CartAddProductForm

@require_POST
def cart_add(request, product_id):
    """Add a product to cart or update its quantity"""
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
                'total_price': cart.get_total_price(),
                'success': True
            }
            return JsonResponse(cart_info)
            
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    """Remove a product from cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_info = {
            'total_items': len(cart),
            'total_price': cart.get_total_price(),
            'success': True
        }
        return JsonResponse(cart_info)
        
    return redirect('cart:cart_detail')

@require_POST
def cart_update(request, product_id):
    """Update quantity of a product in cart"""
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
                'total_price': cart.get_total_price(),
                'item_total': cart.get_item_price(product),
                'success': True
            }
            return JsonResponse(cart_info)
            
    return redirect('cart:cart_detail')

def cart_detail(request):
    """Display cart contents"""
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
    return render(request, 'cart/cart_detail.html', {
        'cart': cart
    })
