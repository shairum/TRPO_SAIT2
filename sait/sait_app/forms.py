from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Review, UserProfile, Trip, TripPhoto

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Электронная почта')
    first_name = forms.CharField(required=True, label='Имя')
    last_name = forms.CharField(required=True, label='Фамилия')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'username': 'Имя пользователя',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user)

        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Расскажите о себе...',
                'style': 'resize: vertical; min-height: 100px;'
            }),
        }
        labels = {
            'avatar': 'Фото профиля',
            'bio': 'О себе',
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Электронная почта')
    first_name = forms.CharField(required=True, label='Имя')
    last_name = forms.CharField(required=True, label='Фамилия')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Имя пользователя',
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Напишите ваш отзыв...'}),
        }
        labels = {
            'rating': 'Ваша оценка',
            'comment': 'Комментарий',
        }

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['title', 'country', 'start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 6}),
        }
        labels = {
            'title': 'Название поездки',
            'country': 'Страна',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'description': 'Рассказ о поездке',
        }