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
from django.template.loader import get_template
import io
from xhtml2pdf import pisa
import requests
from django.conf import settings
from django.http import JsonResponse

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

def product_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    total_quantity = 0
    order_item_exists = False

    if request.method == "POST":
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
            order_item = OrderItem.objects.get(order=order, product=product)
            order_item.quantity = quantity
            order_item.packsize = selected_pack_size
            order_item.price = price * quantity  
            order_item.save()
            print(f'OrderItem updated: Pack Size - {selected_pack_size}, Price - {order_item.price}')
        except OrderItem.DoesNotExist:
            order_item = OrderItem.objects.create(order=order, product=product, quantity=quantity, packsize=selected_pack_size, price=price * quantity)
            print(f'OrderItem created: Pack Size - {selected_pack_size}, Price - {order_item.price}')

        return redirect(reverse('product', kwargs={'slug': slug}))

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


def view_cart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            selected_discounted_price = request.POST.get('selected_discounted_price')
            selected_original_price = request.POST.get('selected_original_price')
            quantity = int(request.POST.get('quantity'))
            order_id = int(request.POST.get('item_id'))

            price = selected_discounted_price if selected_discounted_price else selected_original_price
            order = Order.objects.get(customer=request.user, paid=False)
            order_item = OrderItem.objects.get(id=order_id, order=order)

            order_item.quantity = quantity
            order_item.price = float(price) * int(quantity)
            order_item.save()

    orders = Order.objects.filter(customer=request.user)
    cart_items = OrderItem.objects.filter(order__in=orders)
    
    total_amount = sum(item.price for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'orders': orders
    }
    print(context)
    return render(request, 'cart.html', context)


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
            recipient_list = ['mailto:sagarsavaliya103@gmail.com']
            send_mail(subject, message, sender_email, recipient_list)
            print(sender_email)
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

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

def remove_item_from_cart(request, id):
    cart_item = get_object_or_404(OrderItem, id=id)
    cart_item.delete()
    return redirect('cart')


# def send_whatsapp_message(request):
#     if request.method == 'POST':
#         order_details = request.POST.get('order_details', '')  
#         print(order_details)
#         api_endpoint = 'https://api.whatsapp.com/send'
#         phone_number = settings.WHATSAPP_OWNER_NUMBER  
#         message = f"Order Details:\n{order_details}"
#         whatsapp_url = f"{api_endpoint}?phone={phone_number}&text={message}"
#         try:
#             response = requests.get(whatsapp_url)
#             print(whatsapp_url)
#             response.raise_for_status()  

#             return JsonResponse({'message': 'WhatsApp message sent successfully!', 'order_details':order_details })
#         except requests.exceptions.RequestException as e:
#             return JsonResponse({'error': f'Failed to send WhatsApp message: {str(e)}'}, status=500)
#     else:
#         return JsonResponse({'error': 'Invalid request method'}, status=400)
