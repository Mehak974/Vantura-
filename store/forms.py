"""
Store Forms - All forms with input validation and sanitization.
"""
from django import forms
from django.utils.html import escape
from .models import Review, ContactMessage, Order


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'title', 'comment')
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
                                   attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Review title', 'maxlength': 100}),
            'comment': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4,
                                              'placeholder': 'Share your experience...', 'maxlength': 1000}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        return escape(title)

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '').strip()
        return escape(comment)


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'subject', 'message')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your Name', 'maxlength': 100}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Subject', 'maxlength': 200}),
            'message': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 5,
                                              'placeholder': 'Your message...', 'maxlength': 2000}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name.replace(' ', '').isalpha():
            raise forms.ValidationError("Please enter a valid name (letters only).")
        return escape(name)

    def clean_subject(self):
        return escape(self.cleaned_data.get('subject', '').strip())

    def clean_message(self):
        return escape(self.cleaned_data.get('message', '').strip())


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone', 'address', 'city', 'state', 'country', 'zip_code',
                  'payment_method', 'notes')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Street Address'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'State / Province'}),
            'country': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Country'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ZIP / Postal Code'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2,
                                            'placeholder': 'Order notes (optional)', 'required': False}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        # Enforce valid format: digits, spaces, hyphens, plus sign
        import re
        if not re.match(r'^\+?[\d\s\-()]{7,20}$', phone):
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone

    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code', '').strip()
        if not zip_code.isalnum() or len(zip_code) < 3:
            raise forms.ValidationError("Please enter a valid ZIP / Postal Code.")
        return zip_code

    def clean(self):
        cleaned_data = super().clean()
        from .utils import is_garbage
        
        # Anti-garbage checks for key address fields
        fields_to_check = ['city', 'state', 'country']
        for field in fields_to_check:
            value = cleaned_data.get(field, '')
            if value and is_garbage(value):
                self.add_error(field, f"Please enter a valid {field.replace('_', ' ')}.")

        return cleaned_data
