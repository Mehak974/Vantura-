"""
Accounts Forms - Secure registration and profile forms.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django.utils.html import escape
from .models import UserProfile


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-input', 'placeholder': 'Email Address'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-input'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['class'] = 'form-input'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_first_name(self):
        name = self.cleaned_data.get('first_name', '').strip()
        return escape(name)

    def clean_last_name(self):
        name = self.cleaned_data.get('last_name', '').strip()
        return escape(name)


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input', 'placeholder': 'Username or Email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input', 'placeholder': 'Password'
        })

    def clean(self):
        username = self.cleaned_data.get('username', '').strip()
        password = self.cleaned_data.get('password')

        if username and password:
            # Check if username is actually an email
            if '@' in username:
                try:
                    # Case-insensitive email lookup
                    user_obj = User.objects.get(email__iexact=username)
                    username = user_obj.username
                except User.DoesNotExist:
                    raise forms.ValidationError(
                        "user does not exist",
                        code='invalid_login',
                    )
            else:
                # Check if username exists (case-insensitive for convenience)
                if not User.objects.filter(username__iexact=username).exists():
                    raise forms.ValidationError(
                        "user does not exist",
                        code='invalid_login',
                    )
                # Ensure we use the correct case for authentication
                username = User.objects.get(username__iexact=username).username

            self.user_cache = authenticate(self.request, username=username, password=password)
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    "email or password incorrect",
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input'}))

    class Meta:
        model = UserProfile
        fields = ('phone', 'address', 'city', 'state', 'country', 'zip_code')
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'state': forms.TextInput(attrs={'class': 'form-input'}),
            'country': forms.TextInput(attrs={'class': 'form-input'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-input'}),
        }
