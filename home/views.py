import logging, requests,stripe

logger = logging.getLogger(__name__)

from django.shortcuts import render
from Ecommerce.models import Product, DiscountOffer,UpcomingProduct, Blog, Cart, CartItem,Color,Category, Like, Comment, Order, TeamMember,ContactInfo,Wishlist
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count

def home(request, id=None):
    product_detail = None
    if id:
        product_detail = get_object_or_404(Product, id=id)

    today = timezone.now().date()
    products = Product.objects.filter(
        Q(upcoming__isnull=True) | Q(upcoming__release_date__lte=today)
    )
    current_date = today

    discounts = DiscountOffer.objects.filter(
        start_date__lte=current_date,
        end_date__gte=current_date
    ).select_related('product')

    items = []
    total = Decimal('0.00')

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            items = cart.items.all()
            total = sum(item.product.price * item.quantity for item in items)
            print(f"Authenticated user cart items: {items.count()}")
    else:
        session_cart = request.session.get('cart', {})
        print("Session cart content:", session_cart)
        for product_id_str, quantity in session_cart.items():
            try:
                product_id = int(product_id_str)
                product = Product.objects.get(id=product_id)
                item_total = product.price * quantity
                total += item_total
                items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': item_total
                })
                print(f"Session item: {product.name}, Qty: {quantity}, Total: {item_total}")
            except Product.DoesNotExist:
                print(f"Product {product_id_str} not found.")

    contact = ContactInfo.objects.first()
    upcoming_product = UpcomingProduct.objects.filter(release_date__gte=current_date).first()
    blogs = Blog.objects.order_by('-date_posted')[:3]
    new_products = Product.objects.filter(is_new=True)
    featured_products = Product.objects.filter(Q(label='new') | Q(label='sale'))

    context = {
        'products': products,
        'new_products': new_products,
        'featured_products': featured_products,
        'discounts': discounts,
        'upcoming_product': upcoming_product,
        'blogs': blogs,
        'cart_items': items,
        'cart_total': round(total, 2),
        'product_detail': product_detail,
        'contact': contact
    }
    return render(request, "index-2.html", context)


def register_login(request):
    return render(request,"login.html")

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('home')  # 'home' vaneko default guest page url name ho

def checkout(request):
    return render(request,"checkout.html")

# def cart(request):
#     if request.user.is_authenticated:
#         cart = Cart.objects.filter(user=request.user, is_active=True).first()
#     else:
#         cart_id = request.session.get('cart_id')
#         cart = Cart.objects.filter(id=cart_id, is_active=True).first()

#     cart_items = cart.items.all() if cart else []
#     cart_total = sum(item.product.price * item.quantity for item in cart_items)

#     return render(request, "shop/cart.html", {
#         'cart_items': cart_items,
#         'cart_total': cart_total,
#     })
from decimal import Decimal
from decimal import Decimal
from django.shortcuts import render, redirect
# from .models import Cart, CartItem, Product

def cart(request):
    print("== Cart View ==")
    cart_items = []
    subtotal = Decimal('0.00')
    shipping = Decimal('120.00')

    if request.user.is_authenticated:
        print("User is authenticated:", request.user.username)
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            cart_items = cart.items.all()
            subtotal = sum(item.product.price * item.quantity for item in cart_items)
            print(f"Cart has {cart_items.count()} items")
        else:
            print("No active cart found for user.")
    else:
        print("User is NOT authenticated. Using session-based cart.")
        session_cart = request.session.get('cart', {})
        print("Session cart content:", session_cart)
        for product_id_str, quantity in session_cart.items():
            try:
                product_id = int(product_id_str)
                product = Product.objects.get(id=product_id)
                item_total = product.price * quantity
                subtotal += item_total
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': item_total
                })
                print(f"Added {product.name} x{quantity} to cart_items")
            except Product.DoesNotExist:
                print(f"Product with id {product_id_str} not found. Skipping.")

    total = subtotal + shipping

    # Handle quantity updates
    if request.method == 'POST':
        print("== POST request received: Updating cart quantities ==")
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                try:
                    item_id = int(key.split('_')[1])
                    quantity = int(value)
                    print(f"Updating quantity: item_id={item_id}, quantity={quantity}")
                    if quantity >= 1:
                        if request.user.is_authenticated:
                            cart_item = CartItem.objects.get(id=item_id, cart=cart)
                            cart_item.quantity = quantity
                            cart_item.save()
                        else:
                            # For session cart, update quantity
                            product_id = str(item_id)
                            if product_id in request.session.get('cart', {}):
                                session_cart = request.session['cart']
                                session_cart[product_id] = quantity
                                request.session['cart'] = session_cart
                except Exception as e:
                    print("Error updating quantity:", e)
        return redirect('cart')  # Refresh page after update

    return render(request, "shop/cart.html", {
        'cart_items': cart_items,
        'subtotal': round(subtotal, 2),
        'shipping': round(shipping, 2),
        'total': round(total, 2),
    })


# views.py
from django.shortcuts import get_object_or_404, redirect
# from .models import Product, Cart, CartItem
from django.contrib.auth.decorators import login_required
# views.py

from django.http import JsonResponse

from django.http import JsonResponse,HttpResponse
from django.shortcuts import get_object_or_404
from django.template import RequestContext

def add_to_cart(request, product_id):
    print("Add to cart called for product_id:", product_id)
    product = get_object_or_404(Product, id=product_id)
    print("Product found:", product.name)

    if request.user.is_authenticated:
        print("User is authenticated:", request.user.username)
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
        print(f"Cart fetched or created: {cart}, created={created}")
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += 1
            print("Incremented item quantity to", item.quantity)
        item.save()
        total_quantity = sum(ci.quantity for ci in cart.items.all())
        print("Total quantity in DB cart:", total_quantity)
    else:
        print("User is NOT authenticated. Using session cart.")
        session_cart = request.session.get('cart', {})
        print("Session cart before update:", session_cart)
        session_cart[str(product_id)] = session_cart.get(str(product_id), 0) + 1
        request.session['cart'] = session_cart
        request.session.modified = True  # Important to save session changes
        print("Session cart after update:", request.session['cart'])
        total_quantity = sum(request.session['cart'].values())
        print("Total quantity in session cart:", total_quantity)

    print("Returning JsonResponse with cart_item_count =", total_quantity)
    return JsonResponse({'cart_item_count': total_quantity})

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal


def cart_view(request, id=None):
    print("Cart view called")
    if request.user.is_authenticated:
        print("User authenticated:", request.user.username)
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
        items = cart.items.all()
        subtotal = sum(item.product.price * item.quantity for item in items)
        print(f"Cart items count: {items.count()}, subtotal: {subtotal}")
    else:
        print("User NOT authenticated, loading cart from session")
        session_cart = request.session.get('cart', {})
        print("Session cart content:", session_cart)
        items = []
        subtotal = 0
        for product_id_str, quantity in session_cart.items():
            try:
                product_id = int(product_id_str)
                product = Product.objects.get(pk=product_id)
                item_total = product.price * quantity
                subtotal += item_total
                items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': item_total,
                })
                print(f"Added {product.name} x{quantity} to items, item total: {item_total}")
            except Product.DoesNotExist:
                print(f"Product id {product_id} not found, skipping")

    vat = Decimal('0.00')  # Add VAT logic if you want
    shipping = Decimal('120.00')  # Or dynamic
    total = subtotal + vat + shipping
    print(f"Subtotal: {subtotal}, VAT: {vat}, Shipping: {shipping}, Total: {total}")

    return render(request, 'shop/cart.html', {
        'items': items,
        'subtotal': round(subtotal, 2),
        'shipping': round(shipping, 2),
        'vat': round(vat, 2),
        'total': round(total, 2),
    })

from django.http import JsonResponse
from django.template.loader import render_to_string
def update_cart_mini(request):
    print("update_cart_mini called")
    if request.user.is_authenticated:
        print(f"User is authenticated: {request.user.username}")
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            print(f"Found cart with id: {cart.id}")
            cart_items = cart.items.all()
            print(f"Cart items count: {cart_items.count()}")
        else:
            print("No active cart found for user")
            cart_items = []
    else:
        print("User is NOT authenticated, checking session cart")
        session_cart = request.session.get('cart', {})
        print(f"Session cart data: {session_cart}")
        cart_items = []
        for pid, qty in session_cart.items():
            try:
                product = Product.objects.get(id=pid)
                print(f"Adding product {product.name} with quantity {qty} from session")
                class CartItemDummy:
                    def __init__(self, product, quantity):
                        self.product = product
                        self.quantity = quantity
                cart_items.append(CartItemDummy(product, qty))
            except Product.DoesNotExist:
                print(f"Product with id {pid} does not exist")
                continue

    cart_total = sum(item.product.price * item.quantity for item in cart_items)
    total_quantity = sum(item.quantity for item in cart_items)

    print(f"Total quantity: {total_quantity}")
    print(f"Cart total: {cart_total}")

    mini_cart_html = render_to_string('shop/mini_cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }, request=request)

    return JsonResponse({
        'mini_cart_html': mini_cart_html,
        'cart_item_count': total_quantity,
    })


def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('cart_view')  # Or wherever your cart page is

from decimal import Decimal
from django.shortcuts import render, redirect
# from .models import Cart, Order

from django.shortcuts import redirect
from django.shortcuts import render, redirect
from django.conf import settings
from decimal import Decimal

import stripe
from django.conf import settings
from django.shortcuts import redirect, render
from decimal import Decimal
# from .models import Cart, Order

# Set your secret key
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect
# from .models import Cart, Product, Order

def checkout(request):
    payment_method = request.POST.get('payment_method')  # "stripe" or "khalti"

    cart_items = []
    subtotal = Decimal('0.00')

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            for item in cart.items.all():
                item_total = item.product.price * item.quantity
                cart_items.append({
                    'name': item.product.name,
                    'price': item.product.price,
                    'quantity': item.quantity,
                    'total': item_total
                })
                subtotal += item_total
    else:
        session_cart = request.session.get('cart', {})
        for product_id_str, quantity in session_cart.items():
            try:
                product = Product.objects.get(id=int(product_id_str))
                item_total = product.price * quantity
                cart_items.append({
                    'name': product.name,
                    'price': product.price,
                    'quantity': quantity,
                    'total': item_total
                })
                subtotal += item_total
            except Product.DoesNotExist:
                continue

    shipping = Decimal('120.00')
    vat = Decimal('0.00')
    total = subtotal + shipping + vat

    # Handle POST request (Order placement)
    if request.method == 'POST':
        if not cart_items:
            return redirect('cart')

        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')

        order = Order.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            country=country,
            state=state,
            city=city,
            amount=total
        )

        if request.user.is_authenticated:
            order.user = request.user
            order.save()
            if cart:
                cart.is_active = False
                cart.save()
        else:
            request.session.pop('cart', None)

        if payment_method == 'stripe':
            try:
                token = request.POST.get('stripeToken')
                charge = stripe.Charge.create(
                    amount=int(total * 100),
                    currency='usd',
                    description=f'Payment for order {order.id}',
                    source=token,
                )
                order.payment_status = 'Paid'
                order.save()
                return redirect(f'/checkout?order_id={order.id}')
            except stripe.error.StripeError as e:
                return render(request, 'shop/checkout.html', {
                    'error': str(e),
                    'cart_items': cart_items,
                    'subtotal': round(subtotal, 2),
                    'shipping': round(shipping, 2),
                    'vat': round(vat, 2),
                    'total': round(total, 2),
                    'public_khalti_key': settings.KHALTI_PUBLIC_KEY,
                    'public_key': settings.STRIPE_TEST_PUBLIC_KEY,
                })

        elif payment_method == 'khalti':
            return redirect(f'/checkout?order_id={order.id}')

    # Handle GET request (Show checkout page)
    order_id = request.GET.get('order_id')
    order = Order.objects.filter(id=order_id).first() if order_id else None

    context = {
        'cart_items': cart_items,
        'subtotal': round(subtotal, 2),
        'shipping': round(shipping, 2),
        'vat': round(vat, 2),
        'total': round(total, 2),
        'public_khalti_key': settings.KHALTI_PUBLIC_KEY,
        'public_key': settings.STRIPE_TEST_PUBLIC_KEY,
        'order': order,
    }

    return render(request, 'shop/checkout.html', context)

import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def verify_khalti_payment(request):
    import json
    print("Ok")
    data = json.loads(request.body)

    token = data.get('token')
    print(token)
    amount = data.get('amount')

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}"
    }

    payload = {
        "token": token,
        "amount": amount
    }

    response = requests.post(settings.KHALTI_VERIFY_URL, data=payload, headers=headers)

    if response.status_code == 200:
        # Payment is successful, create Order
        order = Order.objects.create(
            full_name='Khalti User',
            email='n/a',
            phone='n/a',
            address='n/a',
            country='Nepal',
            state='n/a',
            city='n/a',
            amount=Decimal(amount) / 100,
            payment_status='Paid',
        )
        return JsonResponse({"success": True, "order_id": order.id})
    else:
        return JsonResponse({"success": False, "message": response.text})

def account(request):
    return render(request,"account.html")

def contact(request):
    contact = ContactInfo.objects.first()  # या filter गरेर

    return render(request,'contact.html',{'contact': contact})

def aboutus(request):
    team_members = TeamMember.objects.all()

    return render(request,"about.html",{'team_members':team_members})

def shop(request, name):
    template_name = f'shop/{name}.html' 
    return render(request, template_name)


def blog_list(request):
    category_id = request.GET.get('category')  # get category id from URL query param
    categories = Category.objects.all()
    blogs = Blog.objects.annotate(total_likes=Count('likes')).order_by('-date_posted')

    user_liked_blog_ids = []
    if request.user.is_authenticated:
        user_liked_blog_ids = Like.objects.filter(user=request.user).values_list('blog_id', flat=True)
    
    

    if category_id:
        blogs = Blog.objects.filter(category_id=category_id).order_by('-date_posted')
    else:
        blogs = Blog.objects.all().order_by('-date_posted')

    paginator = Paginator(blogs, 9)  # 9 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'blogs': blogs,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None,
        'user_liked_blog_ids': user_liked_blog_ids,
    }
    return render(request, 'blog/blog.html', context)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return str(ip) if ip else '0.0.0.0'  # ✅ Always return string


from django.shortcuts import render, get_object_or_404

from django.shortcuts import render, get_object_or_404, redirect
from Ecommerce.forms import CommentForm

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    comments = blog.comments.all().order_by('-date_posted')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog
            comment.save()
            return redirect('blog_detail', blog_id=blog.id)
    else:
        form = CommentForm()

    return render(request, 'blog/blog_details.html', {
        'blog': blog,
        'form': form,
        'comments': comments,
    })

def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            # If already in wishlist, you might want to remove it (toggle)
            wishlist_item.delete()
            status = 'removed'
        else:
            status = 'added'
        # Count how many wishlist items user has
        count = Wishlist.objects.filter(user=request.user).count()
    else:
        wishlist = request.session.get('wishlist', [])
        if product_id in wishlist:
            wishlist.remove(product_id)
            status = 'removed'
        else:
            wishlist.append(product_id)
            status = 'added'
        request.session['wishlist'] = wishlist
        count = len(wishlist)

    return JsonResponse({'status': status, 'wishlist_count': count})

def wishlist_view(request):
    if request.user.is_authenticated:
        items = Wishlist.objects.filter(user=request.user).select_related('product')
        products = [item.product for item in items]
    else:
        wishlist_ids = request.session.get('wishlist', [])
        products = Product.objects.filter(id__in=wishlist_ids)
    
    return render(request, 'wishlist.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.filter(user=request.user, product=product).delete()
        return JsonResponse({'status': 'removed'})
    return redirect('wishlist_view')  # Redirect if not authenticated

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
# from .models import Order

# @login_required
# def order_history(request):
#     orders = Order.objects.filter(user=request.user).order_by('-created_at')
#     return render(request, 'shop/order_history.html', {'orders': orders})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# from .models import Order

def order_history(request):
    orders = []
    message = None

    if request.user.is_authenticated:
        # Registered user: show their orders
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    elif request.method == 'POST':
        # Guest user: search by phone and email
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        if phone and email:
            orders = Order.objects.filter(user__isnull=True, phone=phone, email=email).order_by('-created_at')
            if not orders.exists():
                message = "No orders found with this phone and email."
        else:
            message = "Please enter both phone and email to track your order."

    return render(request, 'shop/order_history.html', {
        'orders': orders,
        'message': message,
    })


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal
# from .models import Order, CartItem, Cart

@login_required
def order_detail(request, order_id):
    # Get the specific order for the logged-in user
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Find cart for this user (if needed)
    cart = Cart.objects.filter(user=request.user, is_active=False).last()  # Assuming this cart is from that order

    # Get cart items from the most recent inactive cart (adjust logic as needed)
    cart_items = CartItem.objects.filter(cart=cart)

    # Calculate financial summary
    subtotal = sum(item.total for item in cart_items)
    shipping = Decimal('120.00')
    vat = Decimal('0.00')
    total = subtotal + shipping + vat

    return render(request, 'shop/order_detail.html', {
        'order': order,
        'cart_items': cart_items,
        'subtotal': round(subtotal, 2),
        'shipping': round(shipping, 2),
        'vat': round(vat, 2),
        'total': round(total, 2),
    })


def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    colors = Color.objects.all()

    # Filter products by category and color if provided
    category_id = request.GET.get('category')
    color_id = request.GET.get('color')

    if category_id:
        products = products.filter(category__id=category_id)
    if color_id:
        products = products.filter(color__id=color_id)

    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories,
        'colors': colors,
    })
    
from Ecommerce.models import Product, Review
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

# @login_required
# def rate_product(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
    
#     if request.method == 'POST':
#         rating = int(request.POST.get('rating'))
#         comment = request.POST.get('comment', '')
        
#         # Update if already exists, else create
#         review, created = Review.objects.get_or_create(product=product, user=request.user)
#         review.rating = rating
#         review.comment = comment
#         review.save()

#         # Update product average rating
#         all_ratings = product.reviews.all().values_list('rating', flat=True)
#         product.avg_rating = sum(all_ratings) / len(all_ratings)
#         product.save()

#         return redirect(request.META.get('HTTP_REFERER', 'home'))



@login_required
def rate_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')

        # Ensure rating is valid
        if not rating:
            return redirect('home')  # or handle with error

        rating = int(rating)

        # Try to update existing review or create new
        review_qs = Review.objects.filter(product=product, user=request.user)
        if review_qs.exists():
            review = review_qs.first()
            review.rating = rating
            review.comment = comment
            review.save()
        else:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )

        return redirect('home')
