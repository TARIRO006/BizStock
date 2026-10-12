from django import forms
from django.forms import inlineformset_factory
from shops.models import Location
from .models import Product, Category, Supplier, Purchase, PurchaseItem


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



class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier

        fields = [
            'name',
            'contact_person',
            'email',
            'phone',
            'address',
            'notes',
            'is_active',
        ]

        widgets = {

            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. ABC Packaging Supplies',
            }),

            'contact_person': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': "Contact person's name",
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'supplier@example.com',
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+265 ...',
            }),

            'address': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Supplier address...',
            }),

            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Additional information...',
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
                
        }



class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supplier', 'location', 'reference', 'notes']

        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-input'}),
            'location': forms.Select(attrs={'class': 'form-input'}),
            'reference': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. PUR-001',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Optional purchase notes',
            }),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)

        if business is not None:
            self.fields['supplier'].queryset = Supplier.objects.filter(
                business=business,
                is_active=True,
            )
            self.fields['location'].queryset = Location.objects.filter(
                business=business,
                is_active=True,
            )




class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['product', 'quantity', 'unit_cost']

        widgets = {
            'product': forms.Select(attrs={'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0.01',
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0',
            }),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)

        if business is not None:
            self.fields['product'].queryset = Product.objects.filter(
                business=business,
                is_active=True,
            )


PurchaseItemFormSet = inlineformset_factory(
    Purchase,
    PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    can_delete=True,
)

        