from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_verified']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'address')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
