from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import UserRegistrationForm, UserLoginForm
from cart.cart import Cart


def register_view(request):
    if request.user.is_authenticated:
        return redirect('products:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            backend = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user, backend=backend)
            messages.success(request, 'Реєстрацію успішно завершено!')
            
            cart = Cart(request)
            cart.sync_to_db(user)
            
            return redirect('products:home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('products:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                if hasattr(user, 'backend') and user.backend:
                    backend = user.backend
                else:
                    backend = settings.AUTHENTICATION_BACKENDS[0]
                login(request, user, backend=backend)
                name = user.first_name or user.email.split('@')[0]
                messages.success(request, f'Вітаємо, {name}!')
                
                cart = Cart(request)
                cart.sync_to_db(user)
                
                next_url = request.GET.get('next', 'products:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Невірна електронна пошта або пароль.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Выход пользователя"""
    from django.contrib.auth import logout
    
    cart = Cart(request)
    cart.sync_to_session(request.user)
    
    logout(request)
    messages.success(request, 'Ви вийшли з акаунту.')
    return redirect('products:home')
