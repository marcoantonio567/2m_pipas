from django.shortcuts import render

from .models import Product


def product_list(request):
    products = Product.objects.order_by("name")
    return render(request, "produtos.html", {"products": products})
