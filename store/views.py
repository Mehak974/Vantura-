"""
Store Views - All e-commerce views with proper security controls.
"""
import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.utils.html import escape

from .models import (Category, SubCategory, Product, Cart, CartItem,
                     Order, OrderItem, Review, ContactMessage)
from .forms import ReviewForm, ContactForm, CheckoutForm

# Initialize stripe with secret key from settings
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)



# ─── Helper ───────────────────────────────────────────────────────────────────

def get_or_create_cart(request):
    """Get or create cart for user or session."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Merge session cart if exists
        session_key = request.session.session_key
        if session_key:
            session_cart = Cart.objects.filter(session_key=session_key).first()
            if session_cart:
                for item in session_cart.items.all():
                    existing = CartItem.objects.filter(cart=cart, product=item.product).first()
                    if existing:
                        new_qty = existing.quantity + item.quantity
                        existing.quantity = min(new_qty, item.product.stock, 99)
                        existing.save()
                    else:
                        item.cart = cart
                        item.quantity = min(item.quantity, item.product.stock, 99)
                        item.save()
                session_cart.delete()
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart


# ─── Main Pages ───────────────────────────────────────────────────────────────

def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related('category')[:8]
    new_arrivals = Product.objects.filter(is_active=True, is_new=True).select_related('category')[:8]
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/home.html', {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'categories': categories,
    })


def about(request):
    return render(request, 'store/about.html')


@csrf_protect
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent! We\'ll get back to you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ContactForm()
    return render(request, 'store/contact.html', {'form': form})


# ─── Product Views ─────────────────────────────────────────────────────────────

def product_catalog(request):
    products = Product.objects.filter(is_active=True).select_related('category', 'subcategory')
    category_slug = request.GET.get('category')
    subcategory_slug = request.GET.get('subcategory')
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', '-created_at')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    current_category = None
    current_subcategory = None

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=current_category)

    if subcategory_slug and current_category:
        current_subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, category=current_category)
        products = products.filter(subcategory=current_subcategory)

    if search_query:
        terms = search_query.split()
        search_filter = Q()
        for term in terms:
            search_filter &= (
                Q(name__icontains=term) |
                Q(description__icontains=term) |
                Q(category__name__icontains=term) |
                Q(subcategory__name__icontains=term) |
                Q(sku__icontains=term)
            )
        products = products.filter(search_filter)

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

    valid_sorts = ['-created_at', 'price', '-price', 'name', '-name']
    if sort_by in valid_sorts:
        products = products.order_by(sort_by)

    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)

    categories = Category.objects.filter(is_active=True).prefetch_related('subcategories')

    return render(request, 'store/catalog.html', {
        'products': products_page,
        'categories': categories,
        'current_category': current_category,
        'current_subcategory': current_subcategory,
        'search_query': search_query,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'total_count': paginator.count,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).select_related('category').exclude(pk=product.pk)[:4]
    reviews = product.reviews.filter(is_approved=True)
    review_form = ReviewForm()

    user_reviewed = False
    if request.user.is_authenticated:
        user_reviewed = Review.objects.filter(product=product, user=request.user).exists()

    if request.method == 'POST' and request.user.is_authenticated and not user_reviewed:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('product_detail', slug=slug)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'review_form': review_form,
        'user_reviewed': user_reviewed,
    })


# ─── Category Pages ────────────────────────────────────────────────────────────

def category_page(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    subcategory_slug = request.GET.get('subcategory')
    current_subcategory = None

    if subcategory_slug:
        current_subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, category=category)
        products = products.filter(subcategory=current_subcategory)

    paginator = Paginator(products, 12)
    products_page = paginator.get_page(request.GET.get('page', 1))

    template = 'store/category.html'
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'store/includes/product_grid.html'

    return render(request, template, {
        'category': category,
        'products': products_page,
        'current_subcategory': current_subcategory,
        'total_count': paginator.count,
    })


def search(request):
    query = request.GET.get('q', '').strip()
    if query:
        return redirect(f'/products/?q={query}')
    return redirect('catalog')


# ─── Cart Views ────────────────────────────────────────────────────────────────

def cart(request):
    cart_obj = get_or_create_cart(request)
    items = cart_obj.items.select_related('product').all()
    return render(request, 'store/cart.html', {'cart': cart_obj, 'items': items})


def cart_drawer(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_obj = get_or_create_cart(request)
        items = cart_obj.items.select_related('product').all()
        return render(request, 'store/includes/cart_drawer.html', {'cart': cart_obj, 'items': items})
    return redirect('cart')


@require_POST
@csrf_protect
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if not product.in_stock:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Product out of stock'})
        messages.error(request, 'Product is out of stock.')
        return redirect('product_detail', slug=product.slug)

    try:
        quantity = int(request.POST.get('quantity', 1))
        quantity = max(1, min(quantity, 99))  # Clamp between 1-99
    except (ValueError, TypeError):
        quantity = 1

    cart_obj = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart_obj, product=product)
    
    max_qty = min(product.stock, 99)
    if not created:
        item.quantity = min(item.quantity + quantity, max_qty)
    else:
        item.quantity = min(quantity, max_qty)
    item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'"{product.name}" added to cart!',
            'cart_count': cart_obj.total_items
        })
    messages.success(request, f'"{product.name}" added to cart!')
    return redirect('cart')


@require_POST
@csrf_protect
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id)
    # Security: ensure item belongs to current user's cart
    cart_obj = get_or_create_cart(request)
    if item.cart != cart_obj:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    try:
        quantity = int(request.POST.get('quantity', 1))
        quantity = max(1, min(quantity, 99))
    except (ValueError, TypeError):
        quantity = 1

    max_qty = min(item.product.stock, 99)
    item.quantity = min(quantity, max_qty)
    item.save()

    return JsonResponse({
        'success': True,
        'subtotal': float(item.subtotal),
        'cart_total': float(cart_obj.total_price),
        'cart_count': cart_obj.total_items,
    })


@require_POST
@csrf_protect
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id)
    cart_obj = get_or_create_cart(request)
    if item.cart != cart_obj:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    item.delete()
    return JsonResponse({
        'success': True,
        'cart_count': cart_obj.total_items,
        'cart_total': float(cart_obj.total_price),
    })


# ─── Checkout & Orders ─────────────────────────────────────────────────────────

@login_required
@csrf_protect
def checkout(request):
    cart_obj = get_or_create_cart(request)
    items = cart_obj.items.select_related('product').all()

    if not items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.subtotal = cart_obj.total_price
            order.shipping_cost = 0  # Free shipping
            order.total = order.subtotal + order.shipping_cost
            order.save()

            # Create OrderItems immediately for all payment methods
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_price=item.product.price,
                    quantity=item.quantity,
                    subtotal=item.subtotal
                )
            
            # Handle Stripe Payment
            if order.payment_method == 'card':
                try:
                    line_items = []
                    for item in items:
                        product_data = {
                            'name': item.product.name,
                        }
                        if item.product.short_description:
                            product_data['description'] = item.product.short_description

                        line_items.append({
                            'price_data': {
                                'currency': 'usd',
                                'product_data': product_data,
                                'unit_amount': int(item.product.price * 100),
                            },
                            'quantity': item.quantity,
                        })

                    checkout_session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=line_items,
                        mode='payment',
                        success_url=request.build_absolute_uri('/payment/success/') + f'?session_id={{CHECKOUT_SESSION_ID}}&order={order.order_number}',
                        cancel_url=request.build_absolute_uri('/payment/cancel/') + f'?order={order.order_number}',
                        metadata={
                            'order_number': order.order_number,
                            'user_id': request.user.id
                        }
                    )
                    order.stripe_payment_intent_id = checkout_session.id
                    order.save()
                    return redirect(checkout_session.url, code=303)
                except Exception as e:
                    messages.error(request, f"Stripe error: {str(e)}")
                    # Delete the order and items if session creation fails to allow retry
                    order.delete()
                    return redirect('checkout')
            
            else:
                # COD / PayPal / Other logic - mark stock as reduced
                for item in items:
                    item.product.stock = max(0, item.product.stock - item.quantity)
                    item.product.save()

                cart_obj.items.all().delete()
                messages.success(request, f'Order #{order.order_number} placed successfully!')
                return redirect('order_confirmation', order_number=order.order_number)
    else:
        initial = {
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
        }
        form = CheckoutForm(initial=initial)

    return render(request, 'store/checkout.html', {
        'form': form,
        'cart': cart_obj,
        'items': items,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


def payment_success(request):
    session_id = request.GET.get('session_id')
    order_number = request.GET.get('order')
    order = get_object_or_404(Order, order_number=order_number)
    
    # Security: Verify the session with Stripe to prevent manual bypass
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        if checkout_session.payment_status != 'paid':
            messages.error(request, "Payment was not completed successfully.")
            return redirect('checkout')
            
        # Optional: Verify order number in metadata matches
        if checkout_session.metadata.get('order_number') != order_number:
            messages.error(request, "Invalid payment session.")
            return redirect('checkout')
            
    except Exception as e:
        messages.error(request, f"Error verifying payment: {str(e)}")
        return redirect('checkout')

    if not order.payment_status:
        order.payment_status = True
        order.status = 'confirmed'
        order.save()
        
        # Reduce stock for all items in the order
        for item in order.items.all():
            if item.product:
                item.product.stock = max(0, item.product.stock - item.quantity)
                item.product.save()
        
        # Clear the cart
        cart_obj = get_or_create_cart(request)
        cart_obj.items.all().delete()
        
        messages.success(request, "Payment successful! Your order is being processed.")
    
    return redirect('order_confirmation', order_number=order.order_number)


def payment_cancel(request):
    order_number = request.GET.get('order')
    messages.warning(request, "Payment was cancelled. You can try again below.")
    return redirect('checkout')


@login_required
def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_confirmation.html', {'order': order})


# ─── Legal Pages ───────────────────────────────────────────────────────────────

def privacy_policy(request):
    return render(request, 'legal/privacy.html')

def cookies_policy(request):
    return render(request, 'legal/cookies.html')

def terms_conditions(request):
    return render(request, 'legal/terms.html')

def return_exchange(request):
    return render(request, 'legal/return.html')


# ─── Error Handlers ────────────────────────────────────────────────────────────

def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    return render(request, 'errors/500.html', status=500)
