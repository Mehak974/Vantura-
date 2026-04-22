"""
Context Processors - inject cart and categories into every template.
"""
from .models import Category, Cart


def cart_context(request):
    """Inject cart into all templates for the global drawer."""
    cart = None
    items = []
    cart_count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key).first()
        
        if cart:
            cart_count = cart.total_items
            items = cart.items.select_related('product').all()
    except Exception:
        pass
        
    return {
        'cart': cart,
        'items': items,
        'cart_count': cart_count
    }


def categories_context(request):
    """Inject active categories with subcategories into all templates."""
    categories = Category.objects.filter(is_active=True).prefetch_related(
        'subcategories'
    )
    return {'all_categories': categories}
