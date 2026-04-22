"""
Accounts Views - Authentication and profile management.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from .forms import RegisterForm, LoginForm, ProfileForm
from store.models import Order


@csrf_protect
@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Capture guest session key before login flushes it
            guest_session_key = request.session.session_key
            user = form.save()
            login(request, user)
            
            # Merge guest cart into user account
            if guest_session_key:
                from store.models import Cart
                guest_cart = Cart.objects.filter(session_key=guest_session_key).first()
                if guest_cart:
                    guest_cart.merge_with_user(user)

            messages.success(request, f'Welcome to Vantura, {user.first_name}!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/signup.html', {'form': form})


@csrf_protect
@require_http_methods(["GET", "POST"])
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            # Capture guest session key
            guest_session_key = request.session.session_key
            user = form.get_user()
            login(request, user)
            
            # Merge guest cart
            if guest_session_key:
                from store.models import Cart
                guest_cart = Cart.objects.filter(session_key=guest_session_key).first()
                if guest_cart:
                    guest_cart.merge_with_user(user)

            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            pass

    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
@csrf_protect
def profile(request):
    profile_obj = request.user.profile
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:10]

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            # Update User fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile_obj, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })

    return render(request, 'accounts/profile.html', {
        'form': form,
        'orders': orders,
    })
