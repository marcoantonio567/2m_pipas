import unicodedata

from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import Coalesce
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from app.forms import ClientForm
from app.models import Client, SaleItem


def normalize_search_text(value):
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char)).casefold()


class ClientListView(ListView):
    """Lista os clientes com totais de compras e item mais comprado."""

    model = Client
    template_name = "clientes/html/clientes.html"
    context_object_name = "clients"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clients = list(self.object_list)

        context["query"] = self.request.GET.get("q", "").strip()
        context["pagination_query"] = self.get_pagination_query()
        context["total_clients"] = len(clients)
        context["clients_with_sales"] = sum(1 for client in clients if client.total_quantity)
        context["total_items_purchased"] = sum(client.total_quantity for client in clients)
        context["total_clients_spent"] = sum(client.total_spent for client in clients)
        context["pagination_pages"] = self.get_pagination_pages(context)
        return context

    def get_pagination_query(self):
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        return query_params.urlencode()

    def get_pagination_pages(self, context):
        if not context.get("is_paginated"):
            return []
        return [
            page if isinstance(page, int) else "..."
            for page in context["paginator"].get_elided_page_range(
                context["page_obj"].number,
                on_each_side=1,
                on_ends=1,
            )
        ]

    def get_queryset(self):
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

        query = self.request.GET.get("q", "").strip()
        if query:
            normalized_query = normalize_search_text(query)
            matching_client_ids = [
                client_id
                for client_id, name in Client.objects.values_list("id", "name")
                if normalized_query in normalize_search_text(name)
            ]
            clients = clients.filter(id__in=matching_client_ids)

        for client in clients:
            most_purchased = (
                SaleItem.objects.filter(sale__client=client)
                .values("product__name")
                .annotate(total_quantity=Sum("quantity"))
                .order_by("-total_quantity", "product__name")
                .first()
            )
            client.most_purchased_item = most_purchased["product__name"] if most_purchased else "Nenhum"

        return clients


class ClientCreateView(CreateView):
    """Exibe e processa o formulario de cadastro de clientes."""

    model = Client
    form_class = ClientForm
    template_name = "clientes/html/cliente_form.html"
    success_url = reverse_lazy("clientes")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["client"] = None
        return context


class ClientUpdateView(UpdateView):
    """Exibe e processa o formulario de edicao de clientes."""

    model = Client
    form_class = ClientForm
    template_name = "clientes/html/cliente_form.html"
    context_object_name = "client"
    pk_url_kwarg = "client_id"
    success_url = reverse_lazy("clientes")


class ClientDeleteView(DeleteView):
    """Exibe a confirmacao e remove um cliente cadastrado."""

    model = Client
    template_name = "clientes/html/cliente_confirm_delete.html"
    context_object_name = "client"
    pk_url_kwarg = "client_id"
    success_url = reverse_lazy("clientes")
