from django.db import models

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
    age = models.CharField(max_length=3)

    def __str__(self):
        return self.name


class Sale(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="sales")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venda #{self.id} - {self.client.name}"


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
