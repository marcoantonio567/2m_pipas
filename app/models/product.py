from django.db import models


# Representa um produto vendido pela loja, incluindo estoque e precos.
class Product(models.Model):
    STANDARD = "standard"
    LINE = "line"
    PRODUCT_TYPE_CHOICES = [
        (STANDARD, "Produto"),
        (LINE, "Linha"),
    ]

    YARD = "jardas"
    METER = "metros"
    MEASUREMENT_UNIT_CHOICES = [
        (YARD, "Jardas"),
        (METER, "Metros"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=0)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default=STANDARD,
    )
    measurement_unit = models.CharField(
        max_length=10,
        choices=MEASUREMENT_UNIT_CHOICES,
        blank=True,
        default="",
    )
    purchase_measure_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
    )
    sale_piece_size = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
    )

    @property
    def profit_value(self):
        return self.price - self.cost_price

    @property
    def profit_percentage(self):
        if self.price == 0:
            return 0
        return (self.profit_value / self.price) * 100

    @property
    def is_line(self):
        return self.product_type == self.LINE

    @property
    def line_leftover_measure(self):
        if not self.is_line or not self.purchase_measure_quantity or not self.sale_piece_size:
            return 0

        initial_pieces = int(self.purchase_measure_quantity // self.sale_piece_size)
        return self.purchase_measure_quantity - (initial_pieces * self.sale_piece_size)

    @property
    def line_remaining_measure(self):
        if not self.is_line or not self.sale_piece_size:
            return 0

        return (self.quantity * self.sale_piece_size) + self.line_leftover_measure

    def __str__(self):
        return self.name
