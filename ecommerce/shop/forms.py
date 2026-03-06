from django import forms
from .models import Category, Brand, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'stock',
            'category',
            'brand',
            'image',
        ]



class OrderForm(forms.ModelForm):
    class Meta:
        model = __import__('shop').models.Order
        fields = ['full_name', 'email', 'address', 'city']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
