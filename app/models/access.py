from django.db import models


class AccessPassword(models.Model):
    password = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Senha de acesso"
