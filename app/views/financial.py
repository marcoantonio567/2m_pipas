from django.db.models import DecimalField, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from app.forms import FinancialCategoryForm, FinancialTransactionForm
from app.models import FinancialCategory, FinancialTransaction


class DefaultFinancialCategoryMixin:
    def ensure_default_category(self):
        FinancialCategory.objects.get_or_create(name=FinancialCategory.PROTECTED_NAME)


class FinancialCategoryListView(DefaultFinancialCategoryMixin, ListView):
    model = FinancialCategory
    template_name = "financeiro_categorias.html"
    context_object_name = "categories"

    def get_queryset(self):
        self.ensure_default_category()
        return FinancialCategory.objects.all()


class CashRegisterView(DefaultFinancialCategoryMixin, TemplateView):
    template_name = "financeiro_caixa.html"

    def get_context_data(self, **kwargs):
        self.ensure_default_category()
        context = super().get_context_data(**kwargs)
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
        context["transactions"] = transactions
        context["totals"] = totals
        return context


class FinancialTransactionCreateView(DefaultFinancialCategoryMixin, CreateView):
    model = FinancialTransaction
    form_class = FinancialTransactionForm
    template_name = "financeiro_movimentacao_form.html"
    success_url = reverse_lazy("financeiro_caixa")

    def dispatch(self, request, *args, **kwargs):
        self.ensure_default_category()
        return super().dispatch(request, *args, **kwargs)


class FinancialCategoryCreateView(CreateView):
    model = FinancialCategory
    form_class = FinancialCategoryForm
    template_name = "financeiro_categoria_form.html"
    success_url = reverse_lazy("financeiro_categorias")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = None
        return context


class ProtectedCategoryRedirectMixin:
    pk_url_kwarg = "category_id"
    success_url = reverse_lazy("financeiro_categorias")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_protected:
            return redirect("financeiro_categorias")
        return super().dispatch(request, *args, **kwargs)


class FinancialCategoryUpdateView(ProtectedCategoryRedirectMixin, UpdateView):
    model = FinancialCategory
    form_class = FinancialCategoryForm
    template_name = "financeiro_categoria_form.html"
    context_object_name = "category"


class FinancialCategoryDeleteView(ProtectedCategoryRedirectMixin, DeleteView):
    model = FinancialCategory
    template_name = "financeiro_categoria_confirm_delete.html"
    context_object_name = "category"
