from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Client, Product, SaleItem


def product_list(request):
    products = Product.objects.order_by("name")
    return render(request, "produtos.html", {"products": products})


def client_list(request):
    total_spent = ExpressionWrapper(
        F("sales__items__quantity") * F("sales__items__unit_price"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    clients = Client.objects.annotate(
        total_quantity=Coalesce(Sum("sales__items__quantity"), 0),
        total_spent=Coalesce(
            Sum(total_spent),
            0,
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
    ).order_by("name")

    for client in clients:
        most_purchased = (
            SaleItem.objects.filter(sale__client=client)
            .values("product__name")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("-total_quantity", "product__name")
            .first()
        )
        client.most_purchased_item = most_purchased["product__name"] if most_purchased else "Nenhum"

    return render(request, "clientes.html", {"clients": clients})


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


def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.delete()
        return redirect("produtos")

    return render(request, "produto_confirm_delete.html", {"product": product})
