from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class CartItem(models.Model):
    user = models.ForeignKey(
        User,
        related_name='cart_items',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    product = models.ForeignKey(
        Product,
        related_name='cart_items',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField('Количество', default=1)
    created = models.DateTimeField('Добавлено', auto_now_add=True)
    updated = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        ordering = ['-created']
        unique_together = ['user', 'product']  # Один товар в корзине пользователя может быть только один раз

    def __str__(self):
        return f'{self.product.name} - {self.quantity} шт.'

    def get_total_price(self):
        """Получить общую стоимость позиции"""
        return self.product.price * self.quantity
