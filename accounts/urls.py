from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_user, login_user,user_profile
urlpatterns = [
    path('api/register/', register_user, name='register'),
    path('api/login/', login_user, name='login'),
    path('api/user-profile/', user_profile, name='user_profile'),  # Assuming you have a user_profile view
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)