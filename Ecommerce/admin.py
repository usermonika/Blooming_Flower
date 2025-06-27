# admin.py
from django.contrib import admin
from .models import Product,Blog, Category, Color, DiscountOffer, Review, Cart, CartItem, UpcomingProduct, Like,Comment, Tag, Order, TeamMember, ContactInfo

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Color)
admin.site.register(DiscountOffer)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(UpcomingProduct)
admin.site.register(Blog)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(Order)
admin.site.register(TeamMember)
admin.site.register(ContactInfo)