document.addEventListener('DOMContentLoaded', () => {
    // Get CSRF token for AJAX requests
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    // Update cart indicators
    function updateCartIndicators(totalItems, totalPrice) {
        const cartCount = document.getElementById('cartCount');
        const cartTotalElement = document.getElementById('cartTotal');
        
        if (cartCount) cartCount.textContent = totalItems;
        if (cartTotalElement) cartTotalElement.textContent = formatPrice(totalPrice);
    }

    // Format price with Russian locale and currency
    function formatPrice(price) {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 0
        }).format(price);
    }

    // Show notification
    function showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        const notificationText = document.getElementById('notificationText');
        
        if (notification && notificationText) {
            notificationText.textContent = message;
            notification.className = `notification ${type}`;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3500);
        }
    }

    // Add product to cart
    async function addToCart(event) {
        event.preventDefault();
        const form = event.target;
        
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
                showNotification('Товар добавлен в корзину');
            } else {
                showNotification('Не удалось добавить товар', 'error');
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            showNotification('Произошла ошибка', 'error');
        }
    }

    // Update cart quantity
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
                
                // Update row total
                const totalCell = row.querySelector('td.price:last-child');
                if (totalCell) {
                    totalCell.textContent = formatPrice(data.item_total);
                }
                
                // Update cart total
                const cartTotalCell = document.querySelector('tr.total td:last-child');
                if (cartTotalCell) {
                    cartTotalCell.textContent = formatPrice(data.total_price);
                }
            } else {
                showNotification('Не удалось обновить количество', 'error');
            }
        } catch (error) {
            console.error('Error updating quantity:', error);
            showNotification('Произошла ошибка', 'error');
        }
    }

    // Remove item from cart
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
                
                // Update cart total
                const cartTotalCell = document.querySelector('tr.total td:last-child');
                if (cartTotalCell) {
                    cartTotalCell.textContent = formatPrice(data.total_price);
                }
                
                // Show empty cart message if no items left
                if (data.total_items === 0) {
                    const cartTable = document.querySelector('.cart-table');
                    const emptyCart = document.createElement('div');
                    emptyCart.className = 'empty-cart';
                    emptyCart.innerHTML = `
                        <i class="fas fa-shopping-cart"></i>
                        <p>Ваша корзина пуста</p>
                        <a href="/" class="continue-shopping">
                            <i class="fas fa-arrow-left"></i> Перейти к покупкам
                        </a>
                    `;
                    cartTable.replaceWith(emptyCart);
                }
                
                showNotification('Товар удален из корзины');
            } else {
                showNotification('Не удалось удалить товар', 'error');
            }
        } catch (error) {
            console.error('Error removing from cart:', error);
            showNotification('Произошла ошибка', 'error');
        }
    }

    // Event listeners
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', addToCart);
    });

    document.querySelectorAll('.cart-quantity-form').forEach(form => {
        const select = form.querySelector('select');
        if (select) {
            select.addEventListener('change', updateQuantity);
        }
    });

    document.querySelectorAll('.cart-remove-form').forEach(form => {
        form.addEventListener('submit', removeFromCart);
    });
});