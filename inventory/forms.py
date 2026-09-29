from django import forms

from .models import Product, Category


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            'name',
            'category',
            'sku',
            'unit',
            'description',
            'cost_price',
            'selling_price',
            'minimum_stock',
            'is_active',
        ]

        widgets = {

            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Coca Cola 500ml',
                'class': 'form-input',
            }),

            'category': forms.Select(attrs={
                'class': 'form-input',
            }),

            'sku': forms.TextInput(attrs={
                'placeholder': 'e.g. CC500',
                'class': 'form-input',
            }),

            'unit': forms.Select(attrs={
                'class': 'form-input',
            }),

            'description': forms.Textarea(attrs={
                'placeholder': 'Brief description of the product...',
                'rows': 4,
                'class': 'form-input',
            }),

            'cost_price': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'class': 'form-input',
            }),

            'selling_price': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'class': 'form-input',
            }),

            'minimum_stock': forms.NumberInput(attrs={
                'placeholder': '0',
                'step': '0.01',
                'min': '0',
                'class': 'form-input',
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }

    def __init__(self, *args, business=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = Category.objects.filter(
            business=business
        )

        self.fields['category'].empty_label = 'Select a category'



class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category

        fields = [
            'name',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Drinks',
                'class': 'form-input',
            }),
        }