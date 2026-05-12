from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    

class Client(models.Model):
    name = models.CharField(max_length=100)
    age = models.CharField(max_length=3)

    def __str__(self):
        return self.name