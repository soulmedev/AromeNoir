from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('processing', 'Комплектуется'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    user = models.ForeignKey(
        User,
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Пользователь'
    )
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20)
    address = models.CharField('Адрес', max_length=250)
    postal_code = models.CharField('Почтовый индекс', max_length=20)
    city = models.CharField('Город', max_length=100)
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Обновлен', auto_now=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    note = models.TextField('Примечание', blank=True)
    total_price = models.DecimalField(
        'Общая стоимость',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    class Meta:
        ordering = ['-created']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        
    def __str__(self):
        return f'Заказ {self.id}'
        
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
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        related_name='order_items',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Товар'
    )
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=1)
    
    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'
        
    def __str__(self):
        return f'{self.id}'
        
    def get_cost(self):
        return self.price * self.quantity

class DeliveryAddress(models.Model):
    user = models.ForeignKey(
        User,
        related_name='delivery_addresses',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    phone = models.CharField('Телефон', max_length=20)
    address = models.CharField('Адрес', max_length=250)
    postal_code = models.CharField('Почтовый индекс', max_length=20)
    city = models.CharField('Город', max_length=100)
    is_default = models.BooleanField('Основной адрес', default=False)
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'
        ordering = ['-is_default', '-created']

    def __str__(self):
        return f'{self.city}, {self.address}'

    def save(self, *args, **kwargs):
        if self.is_default:
            # Если этот адрес становится основным, убираем флаг у других адресов
            DeliveryAddress.objects.filter(
                user=self.user, 
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)
