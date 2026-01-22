from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('blog/', blog, name='blog'),
    path('services/', services, name='services'),
    path('products/', products, name='products'),
    path('product/<slug:slug>/', product_view, name='product'),
    path('cart/', view_cart, name='cart'),
    path('contact_us/', contact_us, name='contact_us'),
    path('review/<int:product_id>/', login_required(review), name='review'),
    path('delete_cart/<int:id>/', remove_item_from_cart, name='delete_cart'),
    path('update_cart_quantity/', update_cart_quantity, name='update_cart_quantity'),  
    path('generate_invoice/<int:order_id>/', generate_invoice, name='generate_invoice'),
    path('invoice/<int:invoice_id>/', view_invoice, name='view_invoice'),
    path('send_whatsapp_message/', send_whatsapp_message, name='send_whatsapp_message'),
    
    # Order and Payment URLs
    path('create_order/', login_required(create_order), name='create_order'),
    path('select_payment_method/<int:order_id>/', login_required(select_payment_method), name='select_payment_method'),
    path('process_whatsapp_payment/<int:order_id>/', login_required(process_whatsapp_payment), name='process_whatsapp_payment'),
    path('process_online_payment/<int:order_id>/', login_required(process_online_payment), name='process_online_payment'),
    path('payment_success/<int:order_id>/', login_required(payment_success), name='payment_success'),
    path('payment_failed/<int:order_id>/', login_required(payment_failed), name='payment_failed'),
]