from decimal import Decimal
import copy
from django.conf import settings
from products.models import Product
from .models import CartItem


class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.user = request.user if request.user.is_authenticated else None
        
        if not self.user:
            cart = self.session.get(settings.CART_SESSION_ID)
            if not cart:
                cart = self.session[settings.CART_SESSION_ID] = {}
            self.cart = cart
        else:
            self.cart = None

    def add(self, product, quantity=1, override_quantity=False):
        if self.user:
            cart_item, created = CartItem.objects.get_or_create(
                user=self.user,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                if override_quantity:
                    cart_item.quantity = quantity
                else:
                    cart_item.quantity += quantity
                cart_item.save()
        else:
            product_id = str(product.id)
            if product_id not in self.cart:
                self.cart[product_id] = {
                    'quantity': 0,
                    'price': str(product.price)
                }
            if override_quantity:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.cart[product_id]['quantity'] += quantity
            self.save()

    def save(self):
        if not self.user:
            # Переконуємося, що всі ціни збережені як strings, а не Decimal
            for product_id, item_data in self.cart.items():
                if isinstance(item_data.get('price'), (Decimal, float)):
                    item_data['price'] = str(item_data['price'])
            self.session.modified = True

    def remove(self, product):
        if self.user:
            CartItem.objects.filter(user=self.user, product=product).delete()
        else:
            product_id = str(product.id)
            if product_id in self.cart:
                del self.cart[product_id]
                self.save()

    def __iter__(self):
        if self.user:
            cart_items = CartItem.objects.filter(user=self.user).select_related('product')
            for cart_item in cart_items:
                yield {
                    'product': cart_item.product,
                    'quantity': cart_item.quantity,
                    'price': cart_item.product.price,
                    'total_price': cart_item.get_total_price()
                }
        else:
            product_ids = self.cart.keys()
            products = Product.objects.filter(id__in=product_ids)
            # Створюємо глибоку копію, щоб не модифікувати оригінальний словник сесії
            cart = copy.deepcopy(self.cart)
            
            for product in products:
                product_id = str(product.id)
                if product_id in cart:
                    cart[product_id]['product'] = product

            for item in cart.values():
                # Конвертуємо price в Decimal тільки для обчислень, не зберігаємо в сесію
                price = Decimal(item['price'])
                # Створюємо новий словник, щоб не модифікувати копію, яка може мати посилання
                yield {
                    'product': item.get('product'),
                    'quantity': item['quantity'],
                    'price': price,  # Decimal для використання в шаблоні
                    'total_price': price * item['quantity']
                }

    def __len__(self):
        if self.user:
            return sum(item.quantity for item in CartItem.objects.filter(user=self.user))
        else:
            return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        if self.user:
            return sum(
                item.get_total_price()
                for item in CartItem.objects.filter(user=self.user)
            )
        else:
            return sum(
                Decimal(item['price']) * item['quantity']
                for item in self.cart.values()
            )

    def get_item_price(self, product):
        if self.user:
            try:
                cart_item = CartItem.objects.get(user=self.user, product=product)
                return cart_item.get_total_price()
            except CartItem.DoesNotExist:
                return Decimal('0')
        else:
            item = self.cart.get(str(product.id))
            if item:
                return Decimal(item['price']) * item['quantity']
            return Decimal('0')

    def clear(self):
        if self.user:
            CartItem.objects.filter(user=self.user).delete()
        else:
            # Видаляємо кошик з сесії
            if settings.CART_SESSION_ID in self.session:
                del self.session[settings.CART_SESSION_ID]
            # Очищаємо локальну змінну
            self.cart = {}
            # Позначаємо сесію як змінену
            self.session.modified = True

    def sync_to_db(self, user):
        session_cart = self.session.get(settings.CART_SESSION_ID)
        if not session_cart:
            return
        
        for product_id, item_data in session_cart.items():
            try:
                product = Product.objects.get(id=product_id)
                cart_item, created = CartItem.objects.get_or_create(
                    user=user,
                    product=product,
                    defaults={'quantity': item_data['quantity']}
                )
                if not created:
                    cart_item.quantity += item_data['quantity']
                    cart_item.save()
            except Product.DoesNotExist:
                continue
        
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.session.modified = True

    def sync_to_session(self, user):
        cart_items = CartItem.objects.filter(user=user)
        cart = {}
        
        for cart_item in cart_items:
            cart[str(cart_item.product.id)] = {
                'quantity': cart_item.quantity,
                'price': str(cart_item.product.price)
            }
        
        self.session[settings.CART_SESSION_ID] = cart
        self.session.modified = True