from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import Coalesce
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from app.forms import ClientForm
from app.models import Client, SaleItem


class ClientListView(ListView):
    model = Client
    template_name = "clientes.html"
    context_object_name = "clients"

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
    model = Client
    form_class = ClientForm
    template_name = "cliente_form.html"
    success_url = reverse_lazy("clientes")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["client"] = None
        return context


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "cliente_form.html"
    context_object_name = "client"
    pk_url_kwarg = "client_id"
    success_url = reverse_lazy("clientes")


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "cliente_confirm_delete.html"
    context_object_name = "client"
    pk_url_kwarg = "client_id"
    success_url = reverse_lazy("clientes")
