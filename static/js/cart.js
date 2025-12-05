document.addEventListener('DOMContentLoaded', () => {
    let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    if (!csrftoken) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                csrftoken = value;
                break;
            }
        }
    }
    
    console.log('CSRF Token:', csrftoken ? 'Found' : 'Not found');

    function updateCartIndicators(totalItems, totalPrice) {
        const cartCount = document.getElementById('cartCount');
        const cartTotalElement = document.getElementById('cartTotal');
        
        if (cartCount) cartCount.textContent = totalItems;
        if (cartTotalElement) cartTotalElement.textContent = formatPrice(totalPrice);
    }

    function formatPrice(price) {
        const formatter = new Intl.NumberFormat('uk-UA', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        return formatter.format(price) + ' ₴';
    }

    function showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        const notificationText = document.getElementById('notificationText');
        
        if (notification && notificationText) {
            notification.classList.remove('fade-out');
            
            notificationText.textContent = message;
            notification.className = `notification ${type}`;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.add('fade-out');
                setTimeout(() => {
                    notification.classList.remove('show');
                }, 500);
            }, 2000);
        }
    }

    async function addToCart(event) {
        event.preventDefault();
        const form = event.target;
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken || ''
                },
                body: new FormData(form)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                updateCartIndicators(data.total_items, data.total_price);
                showNotification(data.message || 'Товар додано до кошика');
            } else {
                const errorMsg = data.message || 'Не вдалося додати товар';
                console.error('Cart error:', data);
                showNotification(errorMsg, 'error');
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            showNotification(`Помилка: ${error.message}`, 'error');
        }
    }

    async function updateQuantity(event) {
        event.preventDefault();
        const form = event.target.closest('form');
        const row = form.closest('tr');
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                },
                body: new FormData(form)
            });
            
            const data = await response.json();
            
            if (data.success) {
                updateCartIndicators(data.total_items, data.total_price);
                
                const totalCell = row.querySelector('td.price:last-child');
                if (totalCell) {
                    totalCell.textContent = formatPrice(data.item_total);
                }
                
                const cartTotalCell = document.querySelector('tr.total td:last-child');
                if (cartTotalCell) {
                    cartTotalCell.textContent = formatPrice(data.total_price);
                }
            } else {
                showNotification('Не вдалося оновити кількість', 'error');
            }
        } catch (error) {
            console.error('Error updating quantity:', error);
            showNotification('Сталася помилка', 'error');
        }
    }

    async function updateQuantityViaButtons(productId, newQuantity) {
        try {
            const response = await fetch(`/cart/update/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken || '',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `quantity=${newQuantity}`
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                updateCartIndicators(data.total_items, data.total_price);
                
                const row = document.querySelector(`[data-product-id="${productId}"]`)?.closest('tr');
                if (row) {
                    const totalCell = row.querySelector('td.price:last-child');
                    if (totalCell) {
                        totalCell.textContent = formatPrice(data.item_total);
                    }
                }
                
                const cartTotalCell = document.querySelector('tr.total td:last-child');
                if (cartTotalCell) {
                    cartTotalCell.textContent = formatPrice(data.total_price);
                }
                
                showNotification('Кількість оновлена');
            } else {
                showNotification('Не вдалося оновити кількість', 'error');
            }
        } catch (error) {
            console.error('Error updating quantity:', error);
            showNotification('Сталася помилка', 'error');
        }
    }

    async function removeFromCart(event) {
        event.preventDefault();
        const form = event.target;
        const row = form.closest('tr');
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                },
                body: new FormData(form)
            });
            
            const data = await response.json();
            
            if (data.success) {
                row.remove();
                updateCartIndicators(data.total_items, data.total_price);
                
                const cartTotalCell = document.querySelector('tr.total td:last-child');
                if (cartTotalCell) {
                    cartTotalCell.textContent = formatPrice(data.total_price);
                }
                
                if (data.is_empty) {
                    const cartTable = document.querySelector('.cart-table-wrapper');
                    const cartActions = document.querySelector('.cart-actions');
                    const emptyCart = document.createElement('div');
                    emptyCart.className = 'empty-cart';
                    emptyCart.innerHTML = `
                        <i class="fas fa-shopping-bag"></i>
                        <p>Ваш кошик порожній</p>
                        <a href="/products/" class="continue-shopping">
                            <i class="fas fa-arrow-left"></i> Перейти до покупок
                        </a>
                    `;
                    if (cartTable) cartTable.replaceWith(emptyCart);
                    if (cartActions) cartActions.remove();
                }
                
                showNotification('Товар видалено з кошика');
            } else {
                showNotification('Не вдалося видалити товар', 'error');
            }
        } catch (error) {
            console.error('Error removing from cart:', error);
            showNotification('Сталася помилка', 'error');
        }
    }

    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', addToCart);
    });

    document.querySelectorAll('.cart-quantity-form').forEach(form => {
        const select = form.querySelector('select');
        if (select) {
            select.addEventListener('change', updateQuantity);
        }
    });

    document.querySelectorAll('.qty-btn.qty-plus').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const productId = btn.dataset.productId;
            const quantityControl = btn.closest('.quantity-control');
            const input = quantityControl.querySelector('.qty-input');
            let qty = parseInt(input.value) || 1;
            
            if (qty < 20) {
                updateQuantityViaButtons(productId, qty + 1);
                input.value = qty + 1;
            }
        });
    });

    document.querySelectorAll('.qty-btn.qty-minus').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const productId = btn.dataset.productId;
            const quantityControl = btn.closest('.quantity-control');
            const input = quantityControl.querySelector('.qty-input');
            let qty = parseInt(input.value) || 1;
            
            if (qty > 1) {
                updateQuantityViaButtons(productId, qty - 1);
                input.value = qty - 1;
            }
        });
    });

    document.querySelectorAll('.cart-remove-form').forEach(form => {
        form.addEventListener('submit', removeFromCart);
    });
});