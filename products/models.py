from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField('Категория', max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    SCENT_CHOICES = [
        ('floral', 'Floral'),
        ('woody', 'Woody'),
        ('fresh', 'Fresh'),
        ('amber', 'Amber'),
        ('oriental', 'Oriental'),
    ]
    
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория'
    )
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField('Изображение', upload_to='products/')
    description = models.TextField('Описание')
    scent_type = models.CharField('Тип аромата', max_length=20, choices=SCENT_CHOICES)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    available = models.BooleanField('Доступен', default=True)
    is_bestseller = models.BooleanField('Бестселлер', default=False)
    is_exclusive = models.BooleanField('Эксклюзив', default=False)
    is_limited = models.BooleanField('Ограниченная серия', default=False)
    rating = models.DecimalField('Рейтинг', max_digits=2, decimal_places=1, default=5.0)
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-created']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.slug])
    
    def get_badge(self):
        """Возвращает бейдж для товара"""
        if self.is_bestseller:
            return 'Бестселлер'
        elif self.is_exclusive:
            return 'Exclusive'
        elif self.is_limited:
            return 'Limited'
        return None

class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Товар'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Пользователь'
    )
    rating = models.PositiveSmallIntegerField(
        'Оценка',
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    text = models.TextField('Отзыв')
    created = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created']
        unique_together = ['product', 'user']  # Один отзыв на товар от пользователя
        
    def __str__(self):
        return f'Отзыв от {self.user.username} на {self.product.name}'

class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Товар'
    )
    created = models.DateTimeField('Добавлено', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ['-created']
        unique_together = ['user', 'product']
        
    def __str__(self):
        return f'{self.product.name} в избранном у {self.user.username}'