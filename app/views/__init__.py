from .client import ClientCreateView, ClientDeleteView, ClientListView, ClientUpdateView
from .calculator import CalculatorView
from .dashboard import DashboardView
from .financial import (
    CashRegisterView,
    FinancialCategoryCreateView,
    FinancialCategoryDeleteView,
    FinancialCategoryListView,
    FinancialCategoryUpdateView,
    FinancialTransactionCreateView,
    FinancialTransactionDeleteView,
)
from .login import LoginView
from .product import (
    LineProductCreateView,
    ProductCreateView,
    ProductDeleteView,
    ProductListView,
    ProductUpdateView,
)
from .sale import SaleCreateView, SaleDeleteView, SaleListView

__all__ = [
    "CashRegisterView",
    "CalculatorView",
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
    "FinancialTransactionDeleteView",
    "LineProductCreateView",
    "LoginView",
    "ProductCreateView",
    "ProductDeleteView",
    "ProductListView",
    "ProductUpdateView",
    "SaleCreateView",
    "SaleDeleteView",
    "SaleListView",
]
