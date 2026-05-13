from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=0)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def profit_value(self):
        return self.price - self.cost_price

    @property
    def profit_percentage(self):
        if self.cost_price == 0:
            return 0
        return (self.profit_value / self.cost_price) * 100

    def __str__(self):
        return self.name
    

class Client(models.Model):
    name = models.CharField(max_length=100)
    age = models.CharField(max_length=3, blank=True)

    def __str__(self):
        return self.name


class FinancialCategory(models.Model):
    PROTECTED_NAME = "venda"

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Categoria financeira"
        verbose_name_plural = "Categorias financeiras"

    def __str__(self):
        return self.name

    @property
    def is_protected(self):
        return self.name.strip().casefold() == self.PROTECTED_NAME


class FinancialTransaction(models.Model):
    INCOME = "entrada"
    EXPENSE = "saida"
    TYPE_CHOICES = [
        (INCOME, "Entrada"),
        (EXPENSE, "Saida"),
    ]

    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    category = models.ForeignKey(
        FinancialCategory,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    description = models.CharField(max_length=160, blank=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Movimentacao financeira"
        verbose_name_plural = "Movimentacoes financeiras"

    def __str__(self):
        return f"{self.get_type_display()} - R$ {self.amount}"


class Sale(models.Model):
    PIX = "pix"
    CASH = "dinheiro"
    CARD = "cartao"
    PAYMENT_METHOD_CHOICES = [
        (PIX, "Pix"),
        (CASH, "Dinheiro"),
        (CARD, "Cartao"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="sales")
    payment_method = models.CharField(
        max_length=8,
        choices=PAYMENT_METHOD_CHOICES,
        default=PIX,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venda #{self.id} - {self.client.name}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sale_items")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
