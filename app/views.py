from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClientForm, FinancialCategoryForm, ProductForm
from .models import Client, FinancialCategory, Product, SaleItem


def product_list(request):
    products = Product.objects.order_by("name")
    return render(request, "produtos.html", {"products": products})


def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("produtos")
    else:
        form = ProductForm()

    return render(request, "produto_form.html", {"form": form, "product": None})


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


def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("clientes")
    else:
        form = ClientForm()

    return render(request, "cliente_form.html", {"form": form, "client": None})


def financial_category_list(request):
    categories = FinancialCategory.objects.all()
    return render(request, "financeiro_categorias.html", {"categories": categories})


def financial_category_create(request):
    if request.method == "POST":
        form = FinancialCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("financeiro_categorias")
    else:
        form = FinancialCategoryForm()

    return render(request, "financeiro_categoria_form.html", {"form": form, "category": None})


def financial_category_update(request, category_id):
    category = get_object_or_404(FinancialCategory, id=category_id)

    if request.method == "POST":
        form = FinancialCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("financeiro_categorias")
    else:
        form = FinancialCategoryForm(instance=category)

    return render(request, "financeiro_categoria_form.html", {"form": form, "category": category})


def financial_category_delete(request, category_id):
    category = get_object_or_404(FinancialCategory, id=category_id)

    if request.method == "POST":
        category.delete()
        return redirect("financeiro_categorias")

    return render(request, "financeiro_categoria_confirm_delete.html", {"category": category})


def client_update(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("clientes")
    else:
        form = ClientForm(instance=client)

    return render(request, "cliente_form.html", {"form": form, "client": client})


def client_delete(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == "POST":
        client.delete()
        return redirect("clientes")

    return render(request, "cliente_confirm_delete.html", {"client": client})


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
