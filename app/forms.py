from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price"]
        labels = {
            "name": "Nome",
            "description": "Descricao",
            "price": "Preco",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "field", "placeholder": "Nome do produto"}),
            "description": forms.Textarea(
                attrs={
                    "class": "field",
                    "placeholder": "Descricao do produto",
                    "rows": 5,
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "field",
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }
