from django.db.models import DecimalField, Q, Sum
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from app.forms import FinancialCategoryForm, FinancialTransactionForm
from app.models import FinancialCategory, FinancialTransaction


class DefaultFinancialCategoryMixin:
    """Garante que a categoria financeira padrao exista antes de usar as views."""

    def ensure_default_category(self):
        FinancialCategory.objects.get_or_create(name=FinancialCategory.PROTECTED_NAME)


class FinancialCategoryListView(DefaultFinancialCategoryMixin, ListView):
    """Lista as categorias financeiras cadastradas."""

    model = FinancialCategory
    template_name = "financeiro/html/financeiro_categorias.html"
    context_object_name = "categories"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = context["categories"]

        context["total_categories"] = len(categories)
        context["custom_categories"] = sum(1 for category in categories if not category.is_protected)
        context["protected_categories"] = sum(1 for category in categories if category.is_protected)
        return context

    def get_queryset(self):
        self.ensure_default_category()
        return FinancialCategory.objects.all()


class CashRegisterView(DefaultFinancialCategoryMixin, TemplateView):
    """Exibe o caixa com movimentacoes, entradas, saidas e saldo atual."""

    template_name = "financeiro/html/financeiro_caixa.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        self.ensure_default_category()
        context = super().get_context_data(**kwargs)
        transactions = FinancialTransaction.objects.select_related("category")
        paginator = Paginator(transactions, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get("page"))
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
        context["transactions"] = page_obj.object_list
        context["paginator"] = paginator
        context["page_obj"] = page_obj
        context["is_paginated"] = page_obj.has_other_pages()
        context["totals"] = totals
        context["total_transactions"] = transactions.count()
        return context


class FinancialTransactionCreateView(DefaultFinancialCategoryMixin, CreateView):
    """Exibe e processa o formulario de criacao de movimentacoes financeiras."""

    model = FinancialTransaction
    form_class = FinancialTransactionForm
    template_name = "financeiro/html/financeiro_movimentacao_form.html"
    success_url = reverse_lazy("financeiro_caixa")

    def dispatch(self, request, *args, **kwargs):
        self.ensure_default_category()
        return super().dispatch(request, *args, **kwargs)


class FinancialTransactionDeleteView(DeleteView):
    """Exibe a confirmacao e remove uma movimentacao financeira."""

    model = FinancialTransaction
    template_name = "financeiro/html/financeiro_movimentacao_confirm_delete.html"
    context_object_name = "transaction"
    pk_url_kwarg = "transaction_id"
    success_url = reverse_lazy("financeiro_caixa")


class FinancialCategoryCreateView(CreateView):
    """Exibe e processa o formulario de cadastro de categorias financeiras."""

    model = FinancialCategory
    form_class = FinancialCategoryForm
    template_name = "financeiro/html/financeiro_categoria_form.html"
    success_url = reverse_lazy("financeiro_categorias")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = None
        return context


class ProtectedCategoryRedirectMixin:
    """Impede edicao ou exclusao da categoria financeira protegida."""

    pk_url_kwarg = "category_id"
    success_url = reverse_lazy("financeiro_categorias")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_protected:
            return redirect("financeiro_categorias")
        return super().dispatch(request, *args, **kwargs)


class FinancialCategoryUpdateView(ProtectedCategoryRedirectMixin, UpdateView):
    """Exibe e processa o formulario de edicao de categorias financeiras."""

    model = FinancialCategory
    form_class = FinancialCategoryForm
    template_name = "financeiro/html/financeiro_categoria_form.html"
    context_object_name = "category"


class FinancialCategoryDeleteView(ProtectedCategoryRedirectMixin, DeleteView):
    """Exibe a confirmacao e remove uma categoria financeira permitida."""

    model = FinancialCategory
    template_name = "financeiro/html/financeiro_categoria_confirm_delete.html"
    context_object_name = "category"
