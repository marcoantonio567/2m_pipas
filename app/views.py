from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Product


def product_list(request):
    products = Product.objects.order_by("name")
    return render(request, "produtos.html", {"products": products})


def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("produtos")
    else:
        form = ProductForm(instance=product)

    return render(request, "produto_form.html", {"form": form, "product": product})
