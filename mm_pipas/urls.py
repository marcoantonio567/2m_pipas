from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from app.views import (
    CashRegisterView,
    ClientCreateView,
    ClientDeleteView,
    ClientListView,
    ClientUpdateView,
    FinancialCategoryCreateView,
    FinancialCategoryDeleteView,
    FinancialCategoryListView,
    FinancialCategoryUpdateView,
    FinancialTransactionCreateView,
    ProductCreateView,
    ProductDeleteView,
    ProductListView,
    ProductUpdateView,
    SaleCreateView,
    SaleListView,
)

urlpatterns = [
    path('', TemplateView.as_view(template_name='menu.html'), name='menu'),
    path('produtos/', ProductListView.as_view(), name='produtos'),
    path('produtos/novo/', ProductCreateView.as_view(), name='produto_novo'),
    path('clientes/', ClientListView.as_view(), name='clientes'),
    path('clientes/novo/', ClientCreateView.as_view(), name='cliente_novo'),
    path('clientes/<int:client_id>/alterar/', ClientUpdateView.as_view(), name='cliente_alterar'),
    path('clientes/<int:client_id>/excluir/', ClientDeleteView.as_view(), name='cliente_excluir'),
    path('vendas/', SaleListView.as_view(), name='vendas'),
    path('vendas/nova/', SaleCreateView.as_view(), name='venda_nova'),
    path('produtos/<int:product_id>/alterar/', ProductUpdateView.as_view(), name='produto_alterar'),
    path('produtos/<int:product_id>/excluir/', ProductDeleteView.as_view(), name='produto_excluir'),
    path('financeiro/', CashRegisterView.as_view(), name='financeiro_caixa'),
    path('financeiro/movimentacoes/nova/', FinancialTransactionCreateView.as_view(), name='financeiro_movimentacao_nova'),
    path('financeiro/categorias/', FinancialCategoryListView.as_view(), name='financeiro_categorias'),
    path('financeiro/categorias/nova/', FinancialCategoryCreateView.as_view(), name='financeiro_categoria_nova'),
    path('financeiro/categorias/<int:category_id>/alterar/', FinancialCategoryUpdateView.as_view(), name='financeiro_categoria_alterar'),
    path('financeiro/categorias/<int:category_id>/excluir/', FinancialCategoryDeleteView.as_view(), name='financeiro_categoria_excluir'),
    path('admin/', admin.site.urls),
]
