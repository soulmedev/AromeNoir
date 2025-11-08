let cartItems = 0;
let cartTotal = 0;
const cart = [];

function addToCart(productName, price) {
    cartItems++;
    cartTotal += price;
    cart.push({ name: productName, price: price });
    
    document.getElementById('cartCount').textContent = cartItems;
    document.getElementById('notificationText').textContent = `${productName} добавлен в корзину`;
    
    const notification = document.getElementById('notification');
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3500);
}

function showCart() {
    if (cartItems === 0) {
        alert('🛍️ Ваша корзина пуста\n\nИсследуйте нашу эксклюзивную коллекцию ароматов');
    } else {
        let cartDetails = '🛍️ Ваша корзина:\n\n';
        cart.forEach((item, index) => {
            cartDetails += `${index + 1}. ${item.name} — ${item.price.toLocaleString('ru-RU')} ₽\n`;
        });
        cartDetails += `\n━━━━━━━━━━━━━━━━━\n`;
        cartDetails += `Итого: ${cartTotal.toLocaleString('ru-RU')} ₽\n`;
        cartDetails += `Товаров: ${cartItems}`;
        alert(cartDetails);
    }
}