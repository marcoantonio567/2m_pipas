from django.db import models


# Representa um cliente cadastrado para ser vinculado as vendas.
class Client(models.Model):
    name = models.CharField(max_length=100)
    age = models.CharField(max_length=3, blank=True)

    def __str__(self):
        return self.name
