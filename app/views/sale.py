from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, FormView, ListView

from app.forms import SaleForm
from app.models import Client, FinancialCategory, FinancialTransaction, Product, Sale, SaleItem


class SaleListView(ListView):
    """Lista vendas, aplica filtros de busca e calcula totais exibidos na tela."""

    model = Sale
    template_name = "vendas/html/vendas.html"
    context_object_name = "sales"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        payment_method = self.request.GET.get("pagamento", "").strip()
        sales = Sale.objects.select_related("client").prefetch_related("items__product").order_by("-created_at")

        if query:
            sale_filter = Q(client__name__icontains=query) | Q(items__product__name__icontains=query)
            if query.isdigit():
                sale_filter |= Q(id=int(query))
            sales = sales.filter(sale_filter).distinct()

        if payment_method in dict(Sale.PAYMENT_METHOD_CHOICES):
            sales = sales.filter(payment_method=payment_method)

        return sales

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale_list = list(context["sales"])
        context["sales"] = sale_list
        context["payment_methods"] = Sale.PAYMENT_METHOD_CHOICES
        context["selected_payment_method"] = self.request.GET.get("pagamento", "").strip()
        context["query"] = self.request.GET.get("q", "").strip()
        context["pagination_query"] = self.get_pagination_query()
        context["total_revenue"] = sum(sale.total_price for sale in sale_list)
        context["total_items"] = sum(item.quantity for sale in sale_list for item in sale.items.all())

        for sale in sale_list:
            sale.items_summary = ", ".join(
                f"{item.quantity}x {item.product.name}" for item in sale.items.all()
            )

        return context

    def get_pagination_query(self):
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        return query_params.urlencode()


class SaleCreateView(FormView):
    """Registra uma venda, baixa o estoque e cria a movimentacao financeira."""

    form_class = SaleForm
    template_name = "vendas/html/venda_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["clients"] = Client.objects.order_by("name")
        return context

    def form_valid(self, form):
        with transaction.atomic():
            product = Product.objects.select_for_update().get(id=form.cleaned_data["product"].id)
            quantity = form.cleaned_data["quantity"]

            if quantity > product.quantity:
                form.add_error("quantity", f"Estoque insuficiente. Disponivel: {product.quantity}.")
                return self.form_invalid(form)

            client = self.get_or_create_client(form)
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
            self.create_financial_transaction(sale, sale_item, client)

        return redirect("vendas")

    def get_or_create_client(self, form):
        client_name = form.cleaned_data["client_name"]

        client = Client.objects.filter(name__iexact=client_name).first()
        if client is None:
            client = Client.objects.create(name=client_name, age="")
        return client

    def create_financial_transaction(self, sale, sale_item, client):
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


class SaleDeleteView(DeleteView):
    """Exibe a confirmacao e remove uma venda, devolvendo estoque e caixa."""

    model = Sale
    template_name = "vendas/html/venda_confirm_delete.html"
    context_object_name = "sale"
    pk_url_kwarg = "sale_id"
    success_url = reverse_lazy("vendas")

    def form_valid(self, form):
        with transaction.atomic():
            sale = Sale.objects.select_for_update().prefetch_related("items__product").get(
                pk=self.object.pk
            )
            for item in sale.items.all():
                Product.objects.filter(pk=item.product_id).update(
                    quantity=F("quantity") + item.quantity
                )
            FinancialTransaction.objects.filter(
                type=FinancialTransaction.INCOME,
                category__name=FinancialCategory.PROTECTED_NAME,
                description__startswith=f"Venda #{sale.id} -",
            ).delete()
            sale.delete()
        return redirect(self.success_url)
