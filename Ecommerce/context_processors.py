from collections import namedtuple
from .models import Product, Cart, CartItem

def cart_count(request):
    CartObject = namedtuple('CartObject', ['product', 'quantity'])

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        items = cart.items.all() if cart else []
        count = sum(item.quantity for item in items)
        total = sum(item.product.price * item.quantity for item in items)
    else:
        session_cart = request.session.get('cart', {})
        items = []
        count = 0
        total = 0
        for pid, qty in session_cart.items():
            try:
                product = Product.objects.get(id=pid)
                items.append(CartObject(product=product, quantity=qty))
                count += qty
                total += product.price * qty
            except Product.DoesNotExist:
                continue

    return {
        'cart_items': items,
        'cart_item_count': count,
        'cart_total': total
    }
