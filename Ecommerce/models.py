from django.db import models

# Create your models here.
from django.db import models
from accounts.models import CustomUser

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Color Model (e.g., Red, Blue, Green)
class Color(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# Product Model
class Product(models.Model):
    LABEL_CHOICES = (
        ('new', 'New Arrival'),
        ('sale', 'Sale'),
        ('featured', 'Featured'),
        ('', 'Default'),
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    colors = models.ManyToManyField(Color)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    label = models.CharField(max_length=10, choices=LABEL_CHOICES, blank=True, default='')
    # rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)  # eg: 4.5 stars
    sales_count = models.PositiveIntegerField(default=0)  # total sales count
    created_at = models.DateTimeField(auto_now_add=True)
    is_new = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    def __str__(self):
        return self.name

    @property
    def avg_rating(self):
        reviews = self.reviews.all()
        # print("Review count:", reviews.count())  # DEBUG
        if reviews.exists():
            avg = sum(r.rating for r in reviews) / reviews.count()
            return round(avg * 2) / 2
        return 0


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Reference to Django user
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)


class DiscountOffer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='discounts')
    discount_percent = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)  # guest user bhaye null
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Example of what is_active might look like

    
    def __str__(self):
        return f"Cart {self.id}"
    
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Example of what is_active might look like

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
    
    @property
    def total(self):
        return self.product.price * self.quantity
    
class UpcomingProduct(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='upcoming', default=True)
    image = models.ImageField(upload_to='upcoming/')
    release_date = models.DateField()

    def is_now_available(self):
        from django.utils import timezone
        return timezone.now().date() >= self.release_date

class Tag(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/')
    date_posted = models.DateField()
    shares = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='blogs', null=True)

    def __str__(self):
        return self.title

    @property
    def total_likes(self):
        return self.likes.count()

class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='likes')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blog', 'ip_address')  # Only one like per IP per blog

class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=250, default="Unknown")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    message = models.TextField()
    email = models.EmailField(null=True, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user or self.email or self.name} on {self.blog.title}"


# models.py
from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default="Pending")
    is_delivered = models.BooleanField(default=False)

    token = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return f"Order #{self.id} by {self.full_name}"


from django.db import models

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='team/')
    twitter = models.URLField(blank=True, null=True)
    rss = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    pinterest = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class ContactInfo(models.Model):
    address = models.TextField()
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    facebook = models.URLField()
    twitter = models.URLField()
    instagram = models.URLField()

class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
