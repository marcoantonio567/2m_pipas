from django import forms

from .models import Client, FinancialCategory, FinancialTransaction, Product, Sale


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["age"].required = False


class SaleForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.order_by("name"),
        label="Produto",
        empty_label="Escolha um produto",
        widget=forms.Select(attrs={"class": "field"}),
    )
    quantity = forms.IntegerField(
        label="Quantidade",
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                "class": "field",
                "min": "1",
            }
        ),
    )
    client_name = forms.CharField(
        label="Cliente",
        widget=forms.TextInput(
            attrs={
                "class": "field",
                "list": "client-options",
                "autocomplete": "off",
                "placeholder": "Nome do cliente",
            }
        ),
    )
    payment_method = forms.ChoiceField(
        label="Forma de pagamento",
        choices=Sale.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={"class": "field"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        client_name = (cleaned_data.get("client_name") or "").strip()
        product = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity")

        if not client_name:
            self.add_error("client_name", "Informe o nome do cliente.")

        if product and quantity and quantity > product.quantity:
            self.add_error("quantity", f"Estoque insuficiente. Disponivel: {product.quantity}.")

        cleaned_data["client_name"] = client_name
        return cleaned_data


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


class FinancialTransactionForm(forms.ModelForm):
    class Meta:
        model = FinancialTransaction
        fields = ["type", "category", "description", "amount", "date"]
        labels = {
            "type": "Tipo",
            "category": "Categoria",
            "description": "Descricao",
            "amount": "Valor",
            "date": "Data",
        }
        widgets = {
            "type": forms.Select(attrs={"class": "field"}),
            "category": forms.Select(attrs={"class": "field"}),
            "description": forms.TextInput(
                attrs={
                    "class": "field",
                    "placeholder": "Descricao da movimentacao",
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "field",
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "date": forms.DateInput(attrs={"class": "field", "type": "date"}),
        }
