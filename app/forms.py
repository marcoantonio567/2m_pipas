from django import forms

from .models import Client, FinancialCategory, Product


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "age"]
        labels = {
            "name": "Nome",
            "age": "Idade",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "field", "placeholder": "Nome do cliente"}),
            "age": forms.NumberInput(
                attrs={
                    "class": "field",
                    "placeholder": "0",
                    "min": "0",
                    "max": "120",
                }
            ),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "quantity", "cost_price", "price"]
        labels = {
            "name": "Nome",
            "description": "Descricao",
            "quantity": "Quantidade",
            "cost_price": "Preco de custo",
            "price": "Preco de venda",
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
            "quantity": forms.NumberInput(
                attrs={
                    "class": "field",
                    "placeholder": "0",
                    "min": "0",
                }
            ),
            "cost_price": forms.NumberInput(
                attrs={
                    "class": "field",
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0",
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


class FinancialCategoryForm(forms.ModelForm):
    class Meta:
        model = FinancialCategory
        fields = ["name"]
        labels = {
            "name": "Nome",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "field",
                    "placeholder": "Nome da categoria",
                }
            ),
        }
