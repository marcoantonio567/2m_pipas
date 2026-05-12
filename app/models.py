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
