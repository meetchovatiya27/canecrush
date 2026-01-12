from decimal import Decimal
from django.db.models import Case, IntegerField, Value, When
from django.db.models.functions import Cast, Replace
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, OrderItem, ProductPackSize
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Order, OrderItem, Review, Invoice
from .forms import ContactForm, ReviewForm
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.template.loader import get_template
import io
from django.views.decorators.http import require_POST
from xhtml2pdf import pisa
import requests
from django.conf import settings
from django.http import JsonResponse
from urllib.parse import quote

# Create your views here.
def home(request):
    products = Product.objects.all()[:3] 
    rating_range = range(5)
    context = {
        "products": products,
        "rating_range": rating_range,
    }
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')

def blog(request):
    return render(request, 'blog.html')

def products(request):
    products = Product.objects.all()
    context = {
        "products": products,
    }
    return render(request, 'shop.html', context)

@login_required
def product_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    total_quantity = 0
    order_item_exists = False

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to login if not authenticated
            
        selected_product_name = request.POST.get('selected_product_name')
        selected_pack_size = request.POST.get('selected_pack_size')
        selected_discounted_price = request.POST.get('selected_discounted_price')
        quantity = int(request.POST.get('quantity', 1))

        try:
            pack_size_instance = ProductPackSize.objects.get(product=product, pack_size__size=selected_pack_size)
            price = Decimal(selected_discounted_price)
        except ProductPackSize.DoesNotExist:
            price = product.get_discounted_price() 

        order, created = Order.objects.get_or_create(customer=request.user, paid=False)

        try:
            order_item = OrderItem.objects.get(order=order, product=product, packsize=selected_pack_size)
            order_item.quantity += quantity  # Increase quantity instead of replacing
            order_item.price = price * order_item.quantity  
            order_item.save()
            print(f'OrderItem updated: Pack Size - {selected_pack_size}, Price - {order_item.price}')
        except OrderItem.DoesNotExist:
            order_item = OrderItem.objects.create(
                order=order, 
                product=product, 
                quantity=quantity, 
                packsize=selected_pack_size, 
                price=price * quantity
            )
            print(f'OrderItem created: Pack Size - {selected_pack_size}, Price - {order_item.price}')

        return redirect(reverse('cart'))  # Redirect to cart after adding

    else:
        order_item = None
        selected_pack_size = None

        if request.user.is_authenticated:
            order_item = OrderItem.objects.filter(order__customer=request.user, product=product).first()
            if order_item:
                order_item_exists = True
                total_quantity = order_item.quantity
                selected_pack_size = order_item.packsize
                price = order_item.price

        pack_sizes = ProductPackSize.objects.filter(product=product)
        ordered_pack_sizes = pack_sizes.annotate(
            numeric_size=Case(
                When(pack_size__size__icontains='kg', then=Cast(Replace('pack_size__size', Value('kg'), Value('')), IntegerField()) * 1000),
                When(pack_size__size__icontains='g', then=Cast(Replace('pack_size__size', Value('g'), Value('')), IntegerField())),
                output_field=IntegerField()
            )
        ).order_by('numeric_size')

        reviews = Review.objects.filter(product=product)
        form = ReviewForm(initial={'product': product})

        context = {
            'product': product,
            'ordered_pack_sizes': ordered_pack_sizes,
            'order_item_exists': order_item_exists,
            'total_quantity': total_quantity,
            'selected_pack_size': selected_pack_size,
            'reviews': reviews,
            'form': form,
        }

        return render(request, 'product-view.html', context)


def generate_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    total_price = sum(item.price for item in order_items)

    context = {
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
    }

    template = get_template('invoice_template.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order_id}.pdf"'

    pisa_status = pisa.CreatePDF(
       html, dest=response
    )
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required
@require_http_methods(["GET", "POST"])
def view_cart(request):
    # Handle POST requests for quantity updates (legacy support)
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        order_item_id = request.POST.get('item_id')

        if quantity and order_item_id:
            try:
                quantity = int(quantity)
                order_item_id = int(order_item_id)
                
                if quantity < 1:
                    quantity = 1

                order = Order.objects.get(customer=request.user, paid=False)
                order_item = OrderItem.objects.get(id=order_item_id, order=order)
                
                # Get unit price
                unit_price = order_item.price / order_item.quantity if order_item.quantity > 0 else 0
                
                # Update quantity and total price
                order_item.quantity = quantity
                order_item.price = unit_price * quantity
                order_item.save()

            except (TypeError, ValueError, Order.DoesNotExist, OrderItem.DoesNotExist):
                pass

        return redirect('cart')

    # Handle GET requests
    orders = Order.objects.filter(customer=request.user, paid=False)
    cart_items = OrderItem.objects.filter(order__in=orders)

    total_amount = sum(item.price for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'orders': orders
    }

    return render(request, 'cart.html', context)


@login_required
@require_POST
def update_cart_quantity(request):
    """AJAX endpoint to update cart item quantity"""
    try:
        item_id = int(request.POST.get('item_id'))
        quantity = int(request.POST.get('quantity'))
        
        if quantity < 1:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)
        
        # Get the cart item
        order_item = OrderItem.objects.get(
            id=item_id,
            order__customer=request.user,
            order__paid=False
        )
        
        # Check stock
        if quantity > order_item.product.stock:
            return JsonResponse({'error': 'Insufficient stock'}, status=400)
        
        # Calculate unit price
        unit_price = order_item.price / order_item.quantity if order_item.quantity > 0 else 0
        
        # Update quantity and price
        order_item.quantity = quantity
        order_item.price = unit_price * quantity
        order_item.save()
        
        return JsonResponse({
            'success': True,
            'new_total': float(order_item.price),
            'quantity': quantity
        })
        
    except (ValueError, TypeError, OrderItem.DoesNotExist) as e:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    response = HttpResponse(invoice.pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'
    return response

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            subject = f"New contact message from {form.cleaned_data['fname']} {form.cleaned_data['lname']}"
            message = f"From: {form.cleaned_data['fname']} {form.cleaned_data['lname']} <{form.cleaned_data['email']}>\n\nMessage:\n{form.cleaned_data['message']}"
            sender_email = form.cleaned_data['email']
            recipient_list = ['sagarsavaliya103@gmail.com']
            send_mail(subject, message, sender_email, recipient_list)
            print(sender_email)
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

@login_required
def review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.email = request.user.email
            review.product = product
            review.save()
            print("Review saved:", review)
            return redirect('product', slug=product.slug)  
    else:
        form = ReviewForm(initial={'product': product})

    reviews = Review.objects.filter(product=product)
    return render(request, 'product-view.html', {'form': form, 'product': product, 'reviews': reviews})

@require_POST
@login_required
def remove_item_from_cart(request, id):
    """Delete a cart item - uses the URL parameter"""
    cart_item = get_object_or_404(
        OrderItem,
        id=id,
        order__customer=request.user,
        order__paid=False
    )
    cart_item.delete()
    return JsonResponse({'success': True})

@login_required
@require_POST
def send_whatsapp_message(request):
    """Send WhatsApp message with cart details"""
    try:
        order = Order.objects.filter(customer=request.user, paid=False).first()

        if not order:
            return JsonResponse({'error': 'Cart is empty'}, status=400)

        items = OrderItem.objects.filter(order=order)

        if not items.exists():
            return JsonResponse({'error': 'Cart is empty'}, status=400)

        # Build order message with clean structure
        message_parts = []
        message_parts.append("🛒 New Order")
        message_parts.append("━━━━━━━━━━━━━━━━")
        
        total = 0
        for item in items:
            line = f"• {item.product.name} ({item.packsize})\n  Qty: {item.quantity} × ₹{(item.price/item.quantity):.2f} = ₹{item.price:.2f}"
            message_parts.append(line)
            total += item.price
        
        message_parts.append("━━━━━━━━━━━━━━━━")
        message_parts.append(f"💰 Total Amount: ₹{total:.2f}")
        
        # Add customer info if available
        customer_info = []
        if request.user.get_full_name():
            customer_info.append(f"👤 {request.user.get_full_name()}")
        if request.user.email:
            customer_info.append(f"📧 {request.user.email}")
        
        if customer_info:
            message_parts.append("━━━━━━━━━━━━━━━━")
            message_parts.extend(customer_info)
        
        # Join with single newlines (no extra spaces)
        message = "\n".join(message_parts)

        # Get WhatsApp number from settings with fallback
        phone = getattr(settings, 'WHATSAPP_OWNER_NUMBER', None)
        
        if not phone:
            return JsonResponse({
                'error': 'WhatsApp number not configured',
                'message': 'Please add WHATSAPP_OWNER_NUMBER to your settings.py',
                'example': 'WHATSAPP_OWNER_NUMBER = "919876543210"'
            }, status=500)

        # Properly encode the message for URL
        encoded_message = quote(message)
        url = f"https://api.whatsapp.com/send?phone={phone}&text={encoded_message}"

        return JsonResponse({'success': True, 'url': url})
        
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)