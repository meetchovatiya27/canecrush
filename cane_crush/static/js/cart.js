
$(document).ready(function() {
    let totalAmount = 0; 
    let phoneNumber = '9016247243';

    // Futnction to update the quantity
    function updateQuantity(input, delta) {
        let quantity = parseInt(input.val());
        quantity = isNaN(quantity) ? 0 : quantity + delta;
        if (quantity < 1) quantity = 1; 
        input.val(quantity);
        return quantity;
    }
  
    function getProductDetails(container) {
        let input = container.find('.quantity-amount');
        let price = container.closest('tr').find('.product-price').text().trim().replace('₹', '');
        let quantity = input.val();
        let productId = input.data('product-id');
        return {
            productId: productId,
            price: parseFloat(price),
            quantity: parseInt(quantity)
        };
    }

    // Function to update displayed price in input field
    function updateDisplayedPrice(container, newQuantity) {
        let details = getProductDetails(container);
        let totalPrice = details.price * newQuantity;
        container.closest('tr').find('.total-price').text('₹' + totalPrice.toFixed(2));
    }

    function removeFromCart(row) {
        row.remove();
    }
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

        
    // Function to show toast notification
    function showToastNotification(message) {
        var myNotify = new notificationManager({
            container: $('#notificationsContainer'),
            message: message,
            position: "topright",
            type: "info", 
            timeout: 3000 
        });
        myNotify.show();
    }

    $('.quantity-amount').change(function () {
        calculateTotalPrice();
    });
    function updateDisplayedPrice(container, quantity) {
        let price = parseFloat(container.closest('tr').find('.price').text().trim().replace('₹', ''));
        let totalPrice = price * quantity;
        container.closest('tr').find('.total').text(totalPrice.toFixed(2));
        calculateTotalPrice(); 
    }

    function calculateTotalPrice() {
        let subtotal = 0;
        $('.site-blocks-table tbody tr').each(function() {
            let totalText = $(this).find('.total-price span.total').text().replace('₹', '');
            let total = parseFloat(totalText);
            if (!isNaN(total)) {
                subtotal += total;
            }
        });

        $('#subtotal').text(subtotal.toFixed(2));
        $('#total').text(subtotal.toFixed(2));

        totalAmount = subtotal; 
    }
    // Event listener for increase button
    $('.increase').click(function() {
        let container = $(this).closest('.quantity-container');
        let itemstock = container.closest('tr').find('.item-stock').text().trim();
        console.log(itemstock)
        let newQuantity = updateQuantity(container.find('.quantity-amount'), 0); 

        // Disable the increase button if the new quantity equals the stock
        if (newQuantity >= itemstock) {
            $(this).prop('disabled', true);
            showToastNotification('Cannot increase quantity. Maximum stock reached.');
        } 

        updateDisplayedPrice(container, newQuantity);
        calculateTotalPrice();
    });

    // Event listener for decrease button
    $('.decrease').click(function() {
        let container = $(this).closest('.quantity-container');
        let input = container.find('.quantity-amount');

        let itemId = $(this).data('item-id');
        let newQuantity = updateQuantity(input, 0);
        let csrftoken = getCookie('csrftoken');
        let decreaseButton = $(this);
        if (newQuantity < 1) {
            $.ajax({
                url: '/delete_cart/' + itemId + '/',  
                type: 'DELETE',
                headers: {
                    'X-CSRFToken': csrftoken 
                },
                success: function() {
                    console.log("Item removed from cart successfully.");
                    decreaseButton.closest('tr').remove();
                },
                error: function(xhr, status, error) {
                    console.error("Error removing item from cart:", error);
                }
            });
        } else {
            updateDisplayedPrice(container, newQuantity);
            calculateTotalPrice();
            container.find('.increase').prop('disabled', false);
            
        }
    });

     // Form submission handler
     document.getElementById('checkoutForm').addEventListener('submit', function(event) {
        event.preventDefault(); 

        document.querySelectorAll('.quantity-amount').forEach((element, index) => {
            document.getElementsByClassName('hidden-quantity')[index].value = element.value;
        });

        document.querySelectorAll('.total-price span.total').forEach((element, index) => {
            document.getElementsByClassName('hidden-price')[index].value = element.textContent.trim();
        });

        let orderDetails = gatherOrderDetails();
        document.getElementById('orderDetailsField').value = orderDetails;
         
        let message = encodeURIComponent('Hello, I would like to proceed with my order:\n' + orderDetails);
        let whatsappUrl = 'https://wa.me/' + phoneNumber + '?text=' + message;
        
        window.location.href = whatsappUrl;
    });

    // Function to gather order details from the form fields
    function gatherOrderDetails() {
        let orderDetails = [];
        let productNameInputs = document.getElementsByName('product_names[]');
        let quantityInputs = document.getElementsByName('quantities[]');
        let priceInputs = document.getElementsByName('prices[]');

        for (let i = 0; i < productNameInputs.length; i++) {
            let productName = productNameInputs[i].value;
            let quantity = quantityInputs[i].value;
            let price = priceInputs[i].value;
            orderDetails.push(`${productName}: Quantity : ${quantity}, Price : ₹${price}`);
            
        }
        orderDetails.push(`Total Payable amount : ₹${totalAmount}`);
        console.log(orderDetails)
        return orderDetails.join('\n');
    }

    calculateTotalPrice();
});
function redirectToWhatsApp() {
    var message = encodeURIComponent('Hello, I would like to proceed with my order.'); 
    var whatsappUrl = 'https://wa.me/' + phoneNumber + '?text=' + message;
    window.location.href = whatsappUrl;
}

