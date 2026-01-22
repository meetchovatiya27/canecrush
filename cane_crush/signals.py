"""
Signals for automated WhatsApp notifications when payment is approved
"""
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from urllib.parse import quote
from .models import Payment
import threading

# Thread-local storage for old payment status to handle concurrent requests
_thread_local = threading.local()


def get_old_payment_status(payment_id):
    """Get old payment status from thread-local storage"""
    if not hasattr(_thread_local, 'old_payment_statuses'):
        return None
    return _thread_local.old_payment_statuses.get(payment_id)


def set_old_payment_status(payment_id, status):
    """Store old payment status in thread-local storage"""
    if not hasattr(_thread_local, 'old_payment_statuses'):
        _thread_local.old_payment_statuses = {}
    _thread_local.old_payment_statuses[payment_id] = status


@receiver(pre_save, sender=Payment)
def store_old_payment_status(sender, instance, **kwargs):
    """Store the old payment status before save"""
    if instance.pk:
        try:
            old_instance = Payment.objects.get(pk=instance.pk)
            set_old_payment_status(instance.pk, old_instance.status)
        except Payment.DoesNotExist:
            set_old_payment_status(instance.pk, None)
    else:
        set_old_payment_status(None, None)


@receiver(post_save, sender=Payment)
def send_whatsapp_notification_on_payment_approval(sender, instance, created, **kwargs):
    """
    Automatically send WhatsApp notification when:
    1. Payment method is WhatsApp
    2. Payment status changes from 'pending' to 'success'
    """
    # Only process if payment method is WhatsApp
    if instance.payment_method != 'whatsapp':
        return
    
    # Only process if status is 'success'
    if instance.status != 'success':
        return
    
    # Get old status
    old_status = get_old_payment_status(instance.pk) if instance.pk else None
    
    # Check if status changed from 'pending' to 'success'
    # This handles both:
    # 1. Admin changing status from pending to success (old_status == 'pending')
    # 2. New payment created with success status (created == True and old_status is None)
    if created:
        # New payment created with success status - send notification
        should_send = True
    elif old_status == 'pending':
        # Status changed from pending to success - send notification
        should_send = True
    else:
        # Status didn't change from pending, so don't send notification
        should_send = False
    
    if not should_send:
        return
    
    # Check if notification was already sent to prevent duplicates
    if instance.notification_sent:
        return
    
    # Clean up thread-local storage
    if instance.pk and hasattr(_thread_local, 'old_payment_statuses'):
        _thread_local.old_payment_statuses.pop(instance.pk, None)
    
    # Send WhatsApp notification
    whatsapp_url = send_payment_approval_whatsapp(instance)
    
    # Mark notification as sent if URL was generated successfully
    if whatsapp_url:
        # Update notification_sent flag without triggering signals again
        Payment.objects.filter(pk=instance.pk).update(notification_sent=True)


def send_payment_approval_whatsapp(payment):
    """
    Generate WhatsApp URL for payment approval notification and optionally send it
    
    This function generates a WhatsApp message URL that can be:
    1. Used to open WhatsApp web/app with pre-filled message
    2. Sent via WhatsApp Business API (if integrated)
    3. Logged for manual sending
    
    Returns the WhatsApp URL or None if customer phone number is missing
    """
    try:
        order = payment.order
        customer = order.customer
        
        # Build confirmation message
        message_parts = []
        message_parts.append("✅ *Payment Approved!*")
        message_parts.append("━━━━━━━━━━━━━━━━")
        message_parts.append("Your payment has been successfully approved.")
        message_parts.append("")
        message_parts.append(f"📋 *Order ID:* {order.order_id or f'#{order.id}'}")
        message_parts.append(f"💰 *Amount Paid:* ₹{payment.amount:.2f}")
        message_parts.append("")
        message_parts.append("🔄 Your order is now being processed.")
        message_parts.append("")
        message_parts.append("Thank you for your purchase!")
        message_parts.append("We'll notify you once your order is ready for delivery.")
        
        message = "\n".join(message_parts)
        
        # Get customer phone number
        customer_phone = customer.phone_number
        
        if not customer_phone:
            # Log warning if no phone number
            print(f"⚠️ Warning: Customer '{customer.username}' (Order {order.order_id or order.id}) does not have a phone number for WhatsApp notification")
            return None
        
        # Clean phone number (remove +, spaces, dashes, parentheses)
        customer_phone = customer_phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Validate phone number format (should be digits only)
        if not customer_phone.isdigit():
            print(f"⚠️ Warning: Invalid phone number format for customer '{customer.username}': {customer.phone_number}")
            return None
        
        # Encode message for URL
        encoded_message = quote(message)
        
        # Generate WhatsApp URL
        whatsapp_url = f"https://api.whatsapp.com/send?phone={customer_phone}&text={encoded_message}"
        
        # Log the notification (in production, you might want to use Django logging)
        print(f"📱 WhatsApp notification generated for Order {order.order_id or order.id}")
        print(f"   Customer: {customer.username} ({customer_phone})")
        print(f"   URL: {whatsapp_url[:100]}...")
        
        # TODO: Integrate with WhatsApp Business API for automatic sending
        # Example integration with WhatsApp Business API:
        # 
        # from django.conf import settings
        # import requests
        # 
        # if hasattr(settings, 'WHATSAPP_API_TOKEN'):
        #     api_url = "https://graph.facebook.com/v18.0/YOUR_PHONE_NUMBER_ID/messages"
        #     headers = {
        #         "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
        #         "Content-Type": "application/json"
        #     }
        #     payload = {
        #         "messaging_product": "whatsapp",
        #         "to": customer_phone,
        #         "type": "text",
        #         "text": {"body": message}
        #     }
        #     try:
        #         response = requests.post(api_url, json=payload, headers=headers)
        #         response.raise_for_status()
        #         print(f"✅ WhatsApp message sent successfully to {customer_phone}")
        #     except Exception as e:
        #         print(f"❌ Error sending WhatsApp message: {e}")
        
        return whatsapp_url
        
    except Exception as e:
        # Log any errors that occur during notification generation
        print(f"❌ Error generating WhatsApp notification: {e}")
        import traceback
        traceback.print_exc()
        return None

