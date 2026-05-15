from django.db import models


# Representa um produto vendido pela loja, incluindo estoque e precos.
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=0)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    @property
    def profit_value(self):
        return self.price - self.cost_price

    @property
    def profit_percentage(self):
        if self.price == 0:
            return 0
        return (self.profit_value / self.price) * 100

    def __str__(self):
        return self.name
