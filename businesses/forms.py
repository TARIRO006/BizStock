
from django import forms
from .models import Business


class BusinessSettingsForm(forms.ModelForm):

    class Meta:
        model = Business

        fields = [
            'name',
            'business_type',
            'email',
            'phone',
            'address',
            'logo',
            'currency',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter business name',
            }),

            'business_type': forms.Select(attrs={
                'class': 'form-control',
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter business email',
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
            }),

            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter business address',
            }),

            'currency': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
