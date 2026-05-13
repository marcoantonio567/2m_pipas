from django.db import transaction
from django.db.models import DecimalField, ExpressionWrapper, F, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClientForm, FinancialCategoryForm, FinancialTransactionForm, ProductForm, SaleForm
from .models import Client, FinancialCategory, FinancialTransaction, Product, Sale, SaleItem


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
    FinancialCategory.objects.get_or_create(name=FinancialCategory.PROTECTED_NAME)
    categories = FinancialCategory.objects.all()
    return render(request, "financeiro_categorias.html", {"categories": categories})


def cash_register(request):
    FinancialCategory.objects.get_or_create(name=FinancialCategory.PROTECTED_NAME)
    transactions = FinancialTransaction.objects.select_related("category")
    totals = transactions.aggregate(
        income=Coalesce(
            Sum("amount", filter=Q(type=FinancialTransaction.INCOME)),
            0,
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
        expense=Coalesce(
            Sum("amount", filter=Q(type=FinancialTransaction.EXPENSE)),
            0,
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
    )
    totals["balance"] = totals["income"] - totals["expense"]

    return render(
        request,
        "financeiro_caixa.html",
        {
            "transactions": transactions,
            "totals": totals,
        },
    )


def financial_transaction_create(request):
    FinancialCategory.objects.get_or_create(name=FinancialCategory.PROTECTED_NAME)
    if request.method == "POST":
        form = FinancialTransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("financeiro_caixa")
    else:
        form = FinancialTransactionForm()

    return render(request, "financeiro_movimentacao_form.html", {"form": form})


def sale_list(request):
    query = request.GET.get("q", "").strip()
    payment_method = request.GET.get("pagamento", "").strip()
    sales = Sale.objects.select_related("client").prefetch_related("items__product").order_by("-created_at")

    if query:
        sale_filter = Q(client__name__icontains=query) | Q(items__product__name__icontains=query)
        if query.isdigit():
            sale_filter |= Q(id=int(query))
        sales = sales.filter(sale_filter).distinct()

    if payment_method in dict(Sale.PAYMENT_METHOD_CHOICES):
        sales = sales.filter(payment_method=payment_method)

    sale_list_items = list(sales)
    total_revenue = sum(sale.total_price for sale in sale_list_items)
    total_items = sum(item.quantity for sale in sale_list_items for item in sale.items.all())

    for sale in sale_list_items:
        sale.items_summary = ", ".join(
            f"{item.quantity}x {item.product.name}" for item in sale.items.all()
        )

    return render(
        request,
        "vendas.html",
        {
            "sales": sale_list_items,
            "payment_methods": Sale.PAYMENT_METHOD_CHOICES,
            "selected_payment_method": payment_method,
            "query": query,
            "total_revenue": total_revenue,
            "total_items": total_items,
        },
    )


def sale_create(request):
    if request.method == "POST":
        form = SaleForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                product = Product.objects.select_for_update().get(id=form.cleaned_data["product"].id)
                quantity = form.cleaned_data["quantity"]

                if quantity > product.quantity:
                    form.add_error("quantity", f"Estoque insuficiente. Disponivel: {product.quantity}.")
                else:
                    client = form.cleaned_data["client"]
                    client_name = form.cleaned_data["client_name"]

                    if client is None:
                        client = Client.objects.filter(name__iexact=client_name).first()
                        if client is None:
                            client = Client.objects.create(name=client_name, age="")

                    sale = Sale.objects.create(
                        client=client,
                        payment_method=form.cleaned_data["payment_method"],
                    )
                    sale_item = SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        unit_price=product.price,
                    )
                    product.quantity = product.quantity - quantity
                    product.save(update_fields=["quantity"])

                    category, _ = FinancialCategory.objects.get_or_create(
                        name=FinancialCategory.PROTECTED_NAME
                    )
                    FinancialTransaction.objects.create(
                        type=FinancialTransaction.INCOME,
                        category=category,
                        description=(
                            f"Venda #{sale.id} - {client.name} - "
                            f"{sale.get_payment_method_display()}"
                        ),
                        amount=sale_item.total_price,
                    )
                    return redirect("vendas")
    else:
        form = SaleForm()

    return render(request, "venda_form.html", {"form": form})


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
    if category.is_protected:
        return redirect("financeiro_categorias")

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
    if category.is_protected:
        return redirect("financeiro_categorias")

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
