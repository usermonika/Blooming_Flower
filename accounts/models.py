from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES=[
        ('admin','Admin'),
        ('customer', 'Customer'),
    ]
    role= models.CharField(max_length=10,choices=ROLE_CHOICES,default='customer')
    address = models.CharField(max_length=255, blank=True) 
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True,default='profiles/default.png')  # 👈 DEFAULT IMAGE
    is_verified = models.BooleanField(default=True)  # 👈 NEW FIELD

     # Adding related_name to avoid the clash with the default User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Avoids clash with auth.User.groups
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Avoids clash with auth.User.user_permissions
        blank=True
    )
    
    def __str__(self):
        return self.username
