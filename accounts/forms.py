from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label='Електронна пошта',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com'
        })
    )
    first_name = forms.CharField(
        label='Ім\'я',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше ім\'я'
        })
    )
    last_name = forms.CharField(
        label='Прізвище',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше прізвище'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Мінімум 8 символів'
        })
    )
    password2 = forms.CharField(
        label='Підтвердження пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторіть пароль'
        })
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('Користувач з такою електронною поштою вже існує.')
            if User.objects.filter(username=email).exists():
                raise forms.ValidationError('Ця електронна пошта вже використовується.')
        return email

    def save(self, commit=True):
        email = self.cleaned_data['email']
        username = email
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{email}_{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label='Електронна пошта',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть пароль'
        })
    )

