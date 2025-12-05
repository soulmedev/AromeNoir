from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField('Категорія', max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
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
        verbose_name='Категорія'
    )
    name = models.CharField('Назва', max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField('Зображення', upload_to='products/')
    description = models.TextField('Опис')
    scent_type = models.CharField('Тип аромату', max_length=20, choices=SCENT_CHOICES)
    price = models.DecimalField('Ціна', max_digits=10, decimal_places=2)
    available = models.BooleanField('Доступний', default=True)
    is_bestseller = models.BooleanField('Бестселер', default=False)
    is_exclusive = models.BooleanField('Екслюзив', default=False)
    is_limited = models.BooleanField('Обмежена серія', default=False)
    rating = models.DecimalField('Рейтинг', max_digits=2, decimal_places=1, default=5.0)
    created = models.DateTimeField('Створено', auto_now_add=True)
    updated = models.DateTimeField('Оновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
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
        if self.is_bestseller:
            return 'Бестселер'
        elif self.is_exclusive:
            return 'Екслюзив'
        elif self.is_limited:
            return 'Обмежено'
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
        verbose_name='Користувач'
    )
    rating = models.PositiveSmallIntegerField(
        'Оцінка',
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    text = models.TextField('Відгук')
    created = models.DateTimeField('Створено', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'
        ordering = ['-created']
        unique_together = ['product', 'user']
        
    def __str__(self):
        return f'Відгук від {self.user.username} на {self.product.name}'

class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Користувач'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Товар'
    )
    created = models.DateTimeField('Додано', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Обране'
        verbose_name_plural = 'Обране'
        ordering = ['-created']
        unique_together = ['user', 'product']
        
    def __str__(self):
        return f'{self.product.name} в обраному у {self.user.username}'