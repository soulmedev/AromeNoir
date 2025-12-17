from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 
                 'address', 'postal_code', 'city']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Введіть ваше ім\'я'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Введіть ваше прізвище'})
        self.fields['email'].widget.attrs.update({'placeholder': 'example@email.com'})
        self.fields['phone'].widget.attrs.update({'placeholder': '+380 (XX) XXX-XX-XX'})
        self.fields['address'].widget.attrs.update({'placeholder': 'Вулиця, будинок, квартира'})
        self.fields['postal_code'].widget.attrs.update({'placeholder': 'XXXXX'})
        self.fields['city'].widget.attrs.update({'placeholder': 'Назва міста'})