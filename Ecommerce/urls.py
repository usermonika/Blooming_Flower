from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
# # #, register, login, admin_dashboard, customer_dashboard, products_create, customer_list, add_to_cart, cart, checkout,product_details,index

# urlpatterns = [
#     # path('register/',register,name='register'),
#     # path('login/',login,name='login'),
#     # path('admin-dashboard/',admin_dashboard,name='admin-dashboard'),
#     # path('customer-dashboard/',customer_dashboard,name='customer-dashboard'),
#     # path('products-create/',products_create,name='products-create'),
#     # path('customer-list/',customer_list,name='customer_list'),
#     # path('add-cart/',cart, name='cart'),
#     # path('check-out/',checkout, name='checkout'),
#     # path('product-details/',product_details, name='product-details'),
#     # path('index-2/',index,name='index'),
#     # path('cart/',add_to_cart, name='add_to_cart'),
#     ]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)