# models.py
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_save
from accounts.models import AdminUser 

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class PackSize(models.Model):
    PACK_SIZE_CHOICES = (
        ('250g', '250 grams'),
        ('500g', '500 grams'),
        ('1kg', '1 kilogram'),
        ('2kg', '2 kilograms'),
        ('5kg', '5 kilograms'),
    )
    size = models.CharField(max_length=100, choices=PACK_SIZE_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.size


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    main_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image_1 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image_2 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=255, null=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    discount_percentage = models.PositiveIntegerField(blank=True, null=True)
    pack_size = models.ManyToManyField(PackSize, related_name='products', blank=True)

    def get_discounted_price(self):
        if self.discount_percentage:
            discount = self.original_price * (Decimal(self.discount_percentage) / Decimal(100))
            discounted_price = self.original_price - discount
            return discounted_price.quantize(Decimal('.1'), rounding=ROUND_DOWN)
        else:
            return self.original_price.quantize(Decimal('.1'), rounding=ROUND_DOWN)
        
    def get_price_for_pack_size(self, pack_size):
        try:
            product_pack_size = self.product_pack_sizes.get(pack_size=pack_size)
            return product_pack_size.price
        except ProductPackSize.DoesNotExist:
            return None

    def __str__(self):
        return self.name
    
class ProductPackSize(models.Model):
    product = models.ForeignKey(Product, related_name='product_pack_sizes', on_delete=models.CASCADE)
    pack_size = models.ForeignKey(PackSize, related_name='product_pack_sizes', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('product', 'pack_size')

    def get_discounted_price(self):
        if self.product.discount_percentage:
            discount = self.price * (Decimal(self.product.discount_percentage) / Decimal(100))
            discounted_price = self.price - discount
            return round(discounted_price)
        else:
            return self.price.quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
        
    def get_original_price(self):
        return self.price 
        
    def __str__(self):
        return f"{self.product.name} - {self.pack_size.size}"


def create_slug(instance, new_slug=None):
    slug = slugify(instance.name) if new_slug is None else new_slug
    qs = Product.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = f"{slug}-{qs.first().id}"
        return create_slug(instance, new_slug=new_slug)
    return slug


def post_save_product_receiver(sender, instance, created, **kwargs):
    if created and not instance.slug:
        instance.slug = create_slug(instance)
        instance.save()


post_save.connect(post_save_product_receiver, sender=Product)



class Order(models.Model):
    customer = models.ForeignKey(AdminUser, related_name='orders', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f'Order {self.id}'
    
    def remove_items(self):
        self.items.all().delete()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    packsize = models.CharField(max_length=50, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def get_total_price(self):
        return self.price * self.quantity


class Invoice(models.Model):
    user = models.ForeignKey(AdminUser, on_delete=models.CASCADE)
    order = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    pdf = models.FileField(upload_to='invoices/', null=True, blank=True)

    def __str__(self):
        return f"Invoice {self.id} for {self.user.username}"

class ContactMessage(models.Model):
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fname

class Review(models.Model):
    user = models.ForeignKey(AdminUser, related_name='reviews_by_user', on_delete=models.CASCADE)
    email = models.EmailField()
    rating = models.IntegerField()
    review = models.TextField()
    submitted_date = models.DateField(auto_now_add=True) 
    product = models.ForeignKey(Product, related_name='product_review', on_delete=models.CASCADE)

    def __str__(self):
        return f"Review by {self.user.username}"
    
class Payment(models.Model):
    order = models.OneToOneField(Order, related_name='razorpay_payment', on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.FloatField()
    currency = models.CharField(max_length=10, default='INR')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='created')

    def __str__(self):
        return f'Payment {self.payment_id} for Order {self.order.id}'
