from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from app.forms import ProductForm
from app.models import Product


class ProductListView(ListView):
    """Lista os produtos cadastrados em ordem alfabetica."""

    model = Product
    template_name = "produtos/html/produtos.html"
    context_object_name = "products"
    ordering = ["name"]

    def get_queryset(self):
        return Product.objects.filter(is_active=True).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = context["products"]

        context["total_products"] = len(products)
        context["total_quantity"] = sum(product.quantity for product in products)
        context["total_inventory_value"] = sum(product.price * product.quantity for product in products)
        context["total_estimated_profit"] = sum(product.profit_value * product.quantity for product in products)
        return context


class ProductCreateView(CreateView):
    """Exibe e processa o formulario de cadastro de produtos."""

    model = Product
    form_class = ProductForm
    template_name = "produtos/html/produto_form.html"
    success_url = reverse_lazy("produtos")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = None
        return context


class ProductUpdateView(UpdateView):
    """Exibe e processa o formulario de edicao de produtos."""

    model = Product
    form_class = ProductForm
    template_name = "produtos/html/produto_form.html"
    context_object_name = "product"
    pk_url_kwarg = "product_id"
    success_url = reverse_lazy("produtos")


class ProductDeleteView(DeleteView):
    """Remove um produto do catalogo, preservando historico de vendas."""

    model = Product
    template_name = "produtos/html/produto_confirm_delete.html"
    context_object_name = "product"
    pk_url_kwarg = "product_id"
    success_url = reverse_lazy("produtos")

    def form_valid(self, form):
        if self.object.sale_items.exists():
            self.object.is_active = False
            self.object.save(update_fields=["is_active"])
            return redirect(self.success_url)

        try:
            return super().form_valid(form)
        except ProtectedError:
            self.object.is_active = False
            self.object.save(update_fields=["is_active"])
            return redirect(self.success_url)
