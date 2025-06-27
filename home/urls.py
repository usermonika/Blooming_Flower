from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (home ,register_login,logout_view, shop, blog_list, blog_detail,remove_from_cart,
cart,add_to_cart,cart_view,checkout, aboutus, contact, verify_khalti_payment, update_cart_mini,
order_history,order_detail ,wishlist_view,add_to_wishlist,product_detail,remove_from_wishlist,
product_list, rate_product) #, like_blog

urlpatterns = [
    path('',home,name='home'),
    path('product/<int:id>/',home, name='product_quickview'),  # Same view with id
    path('about-us/',aboutus,name='aboutus'),
    path('contact-us/',contact,name='contact'),
    path('register-login/',register_login,name='register_login'),
    path('shop/<str:name>/',shop, name='shop'),
    path('blogs/',blog_list, name='blog_list'),
    path('cart/',cart,name='cart'),
    # path('wishlist/',wishlist,name='wishlist'),
    path('add-to-cart/<int:product_id>/',add_to_cart,name='add_to_cart'),
    path('cart-view/<int:product_id>/',cart_view,name='cart_view'),
    path('cart/remove/<int:item_id>/',remove_from_cart, name='remove_from_cart'),
    path('checkout/',checkout,name='checkout'),
    path('verify-khalti/',verify_khalti_payment, name='verify_khalti_payment'),
    path('logout/',logout_view, name='logout'),
    path('update_cart_mini/',update_cart_mini, name='update_cart_mini'),
    # path('like-blog/<int:blog_id>/',like_blog, name='like_blog'),
    path('blog/<int:blog_id>/',blog_detail, name='blog_detail'),
    path('order-history/', order_history, name='order_history'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('product/<int:id>/',product_detail, name='product_detail'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('product-list/', product_list, name='product_list'),
    path('wishlist-view/', wishlist_view, name='wishlist'),
    path('add-to-wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('product/<int:product_id>/rate/',rate_product, name='rate_product'),

    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)