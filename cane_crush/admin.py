# admin.py
from django.contrib import admin
from .models import Category, Product, Order, OrderItem, PackSize, ContactMessage, Review, Payment, ProductPackSize


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class ProductPackSizeInline(admin.TabularInline):
    model = ProductPackSize
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'stock', 'available')
    list_filter = ('category', 'available')
    search_fields = ('name', 'category__name')
    exclude = ('slug',)
    inlines = [ProductPackSizeInline]
    filter_horizontal = ('pack_size',)

@admin.register(PackSize)
class PackSizeAdmin(admin.ModelAdmin):
    list_display = ('size',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created', 'updated', 'paid')
    list_filter = ('created', 'updated', 'paid')
    search_fields = ('id', 'customer__user__username')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('fname', 'lname', 'email', 'timestamp')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'rating', 'review', 'submitted_date')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('get_customer_username','payment_id', 'amount', 'currency', 'status', 'created_at')
    search_fields = ('payment_id', 'status')
    list_filter = ('status', 'currency', 'created_at')
    ordering = ('-created_at',)
    
    def get_customer_username(self, obj):
        return obj.order.customer.username

    get_customer_username.short_description = 'Customer'

