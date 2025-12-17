from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Min, Max, Avg
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from .models import Product, Category, Review, Favorite
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
    
    category_slug = request.GET.get('category')
    scent_type = request.GET.get('scent_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    badge = request.GET.get('badge')
    sort_by = request.GET.get('sort', 'newest')
    search_query = request.GET.get('search', '')
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if scent_type:
        products = products.filter(scent_type=scent_type)
    
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
    
    if badge == 'bestseller':
        products = products.filter(is_bestseller=True)
    elif badge == 'exclusive':
        products = products.filter(is_exclusive=True)
    elif badge == 'limited':
        products = products.filter(is_limited=True)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-created')
    
    cart_form = CartAddProductForm()
    
    scent_types = Product.SCENT_CHOICES
    
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
    
    # Get reviews
    reviews = Review.objects.filter(product=product).order_by('-created')[:10]
    num_reviews = Review.objects.filter(product=product).count()
    avg_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'] or product.rating
    
    # Check if product is in favorites
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'cart_form': cart_form,
        'reviews': reviews,
        'num_reviews': num_reviews,
        'avg_rating': avg_rating,
        'is_favorite': is_favorite,
        'related_products': related_products,
    })

def about(request):
    return render(request, 'products/about.html')

@login_required
def favorites(request):
    favorites_list = Favorite.objects.filter(user=request.user).select_related('product')
    products = [fav.product for fav in favorites_list if fav.product.available]
    cart_form = CartAddProductForm()
    
    return render(request, 'products/favorite.html', {
        'products': products,
        'cart_form': cart_form,
    })

@login_required
@require_POST
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if not created:
        favorite.delete()
        is_favorite = False
        message = 'Товар видалено з улюблених'
    else:
        is_favorite = True
        message = 'Товар додано до улюблених'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        })
    
    messages.success(request, message)
    return redirect('products:product_detail', slug=product.slug)
