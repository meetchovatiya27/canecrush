from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('blog/', blog, name='blog'),
    path('products/', products, name='products'),
    path('product/<slug:slug>/', product_view, name='product'),
    path('cart/', view_cart, name='cart'),
    path('contact_us/', contact_us, name='contact_us'),
    path('review/<int:product_id>/', login_required(review), name='review'),
    path('delete_cart/<int:id>/', remove_item_from_cart, name='delete_cart'),
    path('update_cart_quantity/', update_cart_quantity, name='update_cart_quantity'),  # NEW - Required for +/- buttons
    path('generate_invoice/<int:order_id>/', generate_invoice, name='generate_invoice'),
    path('invoice/<int:invoice_id>/', view_invoice, name='view_invoice'),
    path('send_whatsapp_message/', send_whatsapp_message, name='send_whatsapp_message'),
    
]