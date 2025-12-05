from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class CartItem(models.Model):
    user = models.ForeignKey(
        User,
        related_name='cart_items',
        on_delete=models.CASCADE,
        verbose_name='Користувач'
    )
    product = models.ForeignKey(
        Product,
        related_name='cart_items',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField('Кількість', default=1)
    created = models.DateTimeField('Додано', auto_now_add=True)
    updated = models.DateTimeField('Оновлено', auto_now=True)

    class Meta:
        verbose_name = 'Товар у кошику'
        verbose_name_plural = 'Товари у кошику'
        ordering = ['-created']
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.product.name} - {self.quantity} шт.'

    def get_total_price(self):
        return self.product.price * self.quantity
