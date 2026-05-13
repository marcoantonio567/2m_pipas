from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


# Agrupa movimentacoes financeiras por tipo de origem ou destino.
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


# Registra entradas e saidas do caixa em uma categoria financeira.
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
