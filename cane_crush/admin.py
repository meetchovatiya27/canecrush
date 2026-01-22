# admin.py
from django.contrib import admin
from django.utils.html import format_html, mark_safe
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

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'packsize', 'price', 'get_total_price')
    can_delete = False
    
    def get_total_price(self, obj):
        return f"₹{obj.get_total_price():.2f}"
    get_total_price.short_description = 'Total'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'id', 'customer', 'get_total_amount', 'created', 'paid', 'get_payment_status')
    list_filter = ('created', 'updated', 'paid')
    search_fields = ('order_id', 'id', 'customer__username', 'customer__email')
    readonly_fields = ('order_id', 'created', 'updated', 'get_total_amount', 'get_payment_info')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'customer', 'created', 'updated', 'paid')
        }),
        ('Order Summary', {
            'fields': ('get_total_amount', 'get_payment_info'),
            'classes': ('collapse',)
        }),
    )
    
    def get_total_amount(self, obj):
        return f"₹{obj.get_total_amount():.2f}"
    get_total_amount.short_description = 'Total Amount'
    
    def get_payment_status(self, obj):
        if hasattr(obj, 'payment'):
            return obj.payment.get_status_display()
        return 'No Payment'
    get_payment_status.short_description = 'Payment Status'
    
    def get_payment_info(self, obj):
        if hasattr(obj, 'payment'):
            payment = obj.payment
            return f"Method: {payment.get_payment_method_display()}\nStatus: {payment.get_status_display()}\nAmount: ₹{payment.amount}\nPayment ID: {payment.payment_id or 'N/A'}"
        return 'No payment record found'
    get_payment_info.short_description = 'Payment Information'

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
    list_display = ('get_order_id', 'get_customer_username', 'payment_method', 'payment_id', 'amount', 'status', 'created_at')
    search_fields = ('payment_id', 'order__order_id', 'order__customer__username', 'order__customer__email')
    list_filter = ('payment_method', 'status', 'currency', 'notification_sent', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('order', 'created_at', 'updated_at', 'notification_sent', 'get_notification_sent_display')
    fieldsets = (
        ('Payment Information', {
            'fields': ('order', 'payment_method', 'payment_id', 'amount', 'currency', 'status')
        }),

        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_paid', 'mark_as_failed', 'resend_whatsapp_notification']
    
    def get_order_id(self, obj):
        return obj.order.order_id or f"Order #{obj.order.id}"
    get_order_id.short_description = 'Order ID'
    
    def get_customer_username(self, obj):
        return obj.order.customer.username
    get_customer_username.short_description = 'Customer'
    
    def get_notification_sent(self, obj):
        """Display notification_sent with green checkmark or red X"""
        if obj.notification_sent:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                '✓ Sent'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>',
                '✗ Not Sent'
            )
    get_notification_sent.short_description = 'Notification Sent'
    get_notification_sent.admin_order_field = 'notification_sent'
    
    def get_notification_sent_display(self, obj):
        """Display notification_sent in detail view with styling"""
        return self.get_notification_sent(obj)
    get_notification_sent_display.short_description = 'Notification Status'
    
    def mark_as_paid(self, request, queryset):
        """Admin action to manually mark payments as paid"""
        updated = 0
        for payment in queryset:
            if payment.status != 'success':
                payment.mark_as_paid()
                updated += 1
        self.message_user(request, f'{updated} payment(s) marked as paid successfully. WhatsApp notifications will be sent automatically.')
    mark_as_paid.short_description = 'Mark selected payments as paid'
    
    def mark_as_failed(self, request, queryset):
        """Admin action to mark payments as failed"""
        queryset.update(status='failed')
        self.message_user(request, f'{queryset.count()} payment(s) marked as failed.')
    mark_as_failed.short_description = 'Mark selected payments as failed'
    
    def resend_whatsapp_notification(self, request, queryset):
        """Admin action to manually resend WhatsApp notifications"""
        from cane_crush.signals import send_payment_approval_whatsapp
        
        sent_count = 0
        failed_count = 0
        
        for payment in queryset:
            if payment.payment_method == 'whatsapp' and payment.status == 'success':
                whatsapp_url = send_payment_approval_whatsapp(payment)
                if whatsapp_url:
                    payment.notification_sent = True
                    payment.save(update_fields=['notification_sent'])
                    sent_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
        

