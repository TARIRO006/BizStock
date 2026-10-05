from django import forms

from .models import Location, Stock
from inventory.models import Product


class LocationForm(forms.ModelForm):

    class Meta:
        model = Location

        fields = [
            'name',
            'location_type',
            'address',
            'phone',
            'is_active',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Main Shop',
                'class': 'form-input',
            }),

            'location_type': forms.Select(attrs={
                'class': 'form-input',
            }),

            'address': forms.Textarea(attrs={
                'placeholder': 'Location address...',
                'rows': 3,
                'class': 'form-input',
            }),

            'phone': forms.TextInput(attrs={
                'placeholder': 'e.g. +265 999 123 456',
                'class': 'form-input',
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }


class StockForm(forms.ModelForm):

    class Meta:
        model = Stock

        fields = [
            'location',
            'product',
            'quantity',
        ]

        widgets = {
            'location': forms.Select(attrs={
                'class': 'form-input',
            }),

            'product': forms.Select(attrs={
                'class': 'form-input',
            }),

            'quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
        }

    def __init__(self, *args, business=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['location'].queryset = Location.objects.filter(
            business=business,
            is_active=True
        )

        self.fields['product'].queryset = Product.objects.filter(
            business=business,
            is_active=True
        )


class StockTransferForm(forms.Form):

    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-input',
        })
    )

    source_location = forms.ModelChoiceField(
        queryset=Location.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-input',
        })
    )

    destination_location = forms.ModelChoiceField(
        queryset=Location.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-input',
        })
    )

    quantity = forms.DecimalField(
        min_value=0.01,
        decimal_places=2,
        max_digits=12,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.01',
        })
    )

    reference = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. TRANS-001',
        })
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Optional notes...',
            'rows': 3,
        })
    )

    def __init__(self, *args, business=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['product'].queryset = Product.objects.filter(
            business=business,
            is_active=True
        )

        self.fields['source_location'].queryset = Location.objects.filter(
            business=business,
            is_active=True
        )

        self.fields['destination_location'].queryset = Location.objects.filter(
            business=business,
            is_active=True
        )

    def clean(self):

        cleaned_data = super().clean()

        source = cleaned_data.get('source_location')
        destination = cleaned_data.get('destination_location')

        if source and destination and source == destination:
            raise forms.ValidationError(
                'Source and destination locations must be different.'
            )

        return cleaned_data