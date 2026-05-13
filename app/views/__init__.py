from .client import ClientCreateView, ClientDeleteView, ClientListView, ClientUpdateView
from .dashboard import DashboardView
from .financial import (
    CashRegisterView,
    FinancialCategoryCreateView,
    FinancialCategoryDeleteView,
    FinancialCategoryListView,
    FinancialCategoryUpdateView,
    FinancialTransactionCreateView,
)
from .product import ProductCreateView, ProductDeleteView, ProductListView, ProductUpdateView
from .sale import SaleCreateView, SaleListView

__all__ = [
    "CashRegisterView",
    "ClientCreateView",
    "ClientDeleteView",
    "ClientListView",
    "ClientUpdateView",
    "DashboardView",
    "FinancialCategoryCreateView",
    "FinancialCategoryDeleteView",
    "FinancialCategoryListView",
    "FinancialCategoryUpdateView",
    "FinancialTransactionCreateView",
    "ProductCreateView",
    "ProductDeleteView",
    "ProductListView",
    "ProductUpdateView",
    "SaleCreateView",
    "SaleListView",
]
