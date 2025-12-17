from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На обробці'),
        ('processing', 'Комплектується'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Відмінено'),
    ]
    
    user = models.ForeignKey(
        User,
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Користувач'
    )
    first_name = models.CharField('Ім\'я', max_length=50)
    last_name = models.CharField('Прізвище', max_length=50)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20)
    address = models.CharField('Адреса', max_length=250)
    postal_code = models.CharField('Поштовий індекс', max_length=20)
    city = models.CharField('Місто', max_length=100)
    created = models.DateTimeField('Створено', auto_now_add=True)
    updated = models.DateTimeField('Оновлено', auto_now=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    note = models.TextField('Примітка', blank=True)
    total_price = models.DecimalField(
        'Загальна вартість',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    paid = models.BooleanField('Оплачено', default=False)
    stripe_payment_intent_id = models.CharField(
        'Stripe Payment Intent ID',
        max_length=255,
        blank=True,
        null=True
    )
    
    class Meta:
        ordering = ['-created']
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        
    def __str__(self):
        return f'Замовлення {self.id}'
        
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
        
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.get_total_cost()
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name='Замовлення'
    )
    product = models.ForeignKey(
        Product,
        related_name='order_items',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Товар'
    )
    price = models.DecimalField('Ціна', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Кількість', default=1)
    
    class Meta:
        verbose_name = 'Товар у замовленні'
        verbose_name_plural = 'Товари у замовленні'
        
    def __str__(self):
        return f'{self.id}'
        
    def get_cost(self):
        return self.price * self.quantity