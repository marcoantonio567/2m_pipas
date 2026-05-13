from django.db import models

from .client import Client
from .product import Product


# Representa uma venda feita para um cliente e sua forma de pagamento.
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


# Representa cada produto incluido em uma venda, com quantidade e preco unitario.
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
