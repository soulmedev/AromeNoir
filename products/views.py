from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from cart.forms import CartAddProductForm

def home(request):
    """Главная страница"""
    products = Product.objects.filter(available=True)[:6]
    cart_form = CartAddProductForm()
    return render(request, 'products/home.html', {
        'products': products,
        'cart_form': cart_form
    })

def product_list(request, category_slug=None):
    """Список товаров"""
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    cart_form = CartAddProductForm()
    return render(request, 'products/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'cart_form': cart_form
    })

def product_detail(request, slug):
    """Детальная страница товара"""
    product = get_object_or_404(Product, slug=slug, available=True)
    cart_form = CartAddProductForm()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'cart_form': cart_form
    })