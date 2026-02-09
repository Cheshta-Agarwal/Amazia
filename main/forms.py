from django import forms

from .models import Order, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'description',
            'price',
            'stock',
            'image_url',
            'is_active',
            'featured',
            'colorway',
            'sizes',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'sizes': forms.TextInput(attrs={'placeholder': 'XS,S,M,L,XL'}),
        }


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
