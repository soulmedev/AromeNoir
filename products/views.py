from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min, Max
from .models import Product, Category
from cart.forms import CartAddProductForm

def home(request):
    products = Product.objects.filter(available=True)[:6]
    cart_form = CartAddProductForm()
    return render(request, 'products/home.html', {
        'products': products,
        'cart_form': cart_form
    })

def collection(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    # Фільтри
    category_slug = request.GET.get('category')
    scent_type = request.GET.get('scent_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    badge = request.GET.get('badge')
    sort_by = request.GET.get('sort', 'newest')
    search_query = request.GET.get('search', '')
    
    # Фільтр по категорії
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Фільтр по типу аромату
    if scent_type:
        products = products.filter(scent_type=scent_type)
    
    # Фільтр по ціні
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Фільтр по бейджу
    if badge == 'bestseller':
        products = products.filter(is_bestseller=True)
    elif badge == 'exclusive':
        products = products.filter(is_exclusive=True)
    elif badge == 'limited':
        products = products.filter(is_limited=True)
    
    # Пошук
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Сортування
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    else:  # newest
        products = products.order_by('-created')
    
    cart_form = CartAddProductForm()
    
    # Отримуємо унікальні типи ароматів для фільтра
    scent_types = Product.SCENT_CHOICES
    
    # Отримуємо мінімальну та максимальну ціни для діапазону
    all_products = Product.objects.filter(available=True)
    price_range = all_products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    ) if all_products.exists() else {'min_price': 0, 'max_price': 10000}
    
    context = {
        'products': products,
        'categories': categories,
        'scent_types': scent_types,
        'cart_form': cart_form,
        'selected_category': category_slug,
        'selected_scent_type': scent_type,
        'selected_badge': badge,
        'selected_sort': sort_by,
        'search_query': search_query,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'price_range': price_range,
    }
    
    return render(request, 'products/collection.html', context)

def product_list(request, category_slug=None):
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
    product = get_object_or_404(Product, slug=slug, available=True)
    cart_form = CartAddProductForm()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'cart_form': cart_form
    })

def about(request):
    return render(request, 'products/about.html')