from decimal import Decimal, ROUND_FLOOR

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
        queryset=Product.objects.filter(is_active=True).order_by("name"),
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


class LineProductForm(forms.ModelForm):
    total_cost = forms.DecimalField(
        label="Preco de custo total",
        min_value=Decimal("0.01"),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "field line-calculation-field",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0.01",
            }
        ),
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "measurement_unit",
            "purchase_measure_quantity",
            "sale_piece_size",
            "total_cost",
            "price",
        ]
        labels = {
            "name": "Nome da linha",
            "description": "Descricao",
            "measurement_unit": "Unidade de medida",
            "purchase_measure_quantity": "tamanho comprada",
            "sale_piece_size": "Tamanho do pedaco de venda",
            "price": "Preco de venda por pedaco",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "field", "placeholder": "Nome da linha"}),
            "description": forms.Textarea(
                attrs={
                    "class": "field",
                    "placeholder": "Descricao da linha",
                    "rows": 5,
                }
            ),
            "measurement_unit": forms.Select(attrs={"class": "field line-calculation-field"}),
            "purchase_measure_quantity": forms.NumberInput(
                attrs={
                    "class": "field line-calculation-field",
                    "placeholder": "0",
                    "step": "0.001",
                    "min": "0.001",
                }
            ),
            "sale_piece_size": forms.NumberInput(
                attrs={
                    "class": "field line-calculation-field",
                    "placeholder": "0",
                    "step": "0.001",
                    "min": "0.001",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["measurement_unit"].required = True
        self.fields["purchase_measure_quantity"].required = True
        self.fields["sale_piece_size"].required = True

    def clean(self):
        cleaned_data = super().clean()
        purchase_quantity = cleaned_data.get("purchase_measure_quantity")
        piece_size = cleaned_data.get("sale_piece_size")

        if purchase_quantity and piece_size and piece_size > purchase_quantity:
            self.add_error(
                "sale_piece_size",
                "O tamanho do pedaco nao pode ser maior que a quantidade comprada.",
            )

        return cleaned_data

    def save(self, commit=True):
        product = super().save(commit=False)
        total_cost = self.cleaned_data["total_cost"]
        purchase_quantity = self.cleaned_data["purchase_measure_quantity"]
        piece_size = self.cleaned_data["sale_piece_size"]

        product.product_type = Product.LINE
        product.quantity = int((purchase_quantity / piece_size).to_integral_value(rounding=ROUND_FLOOR))
        product.cost_price = ((total_cost / purchase_quantity) * piece_size).quantize(Decimal("0.01"))

        if commit:
            product.save()
        return product


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
