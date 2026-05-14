from decimal import Decimal
from collections import defaultdict

from django.db.models import DecimalField, Q, Sum
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone
from django.views.generic import TemplateView

from app.models import FinancialTransaction, Sale, SaleItem


class DashboardView(TemplateView):
    """Exibe indicadores consolidados de vendas, financeiro e lucro."""

    template_name = "dashboards/html/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        weekday_sales = self.get_weekday_sales()
        top_products = self.get_top_products_by_quantity()
        top_profit_products = self.get_top_products_by_profit()
        payment_methods = self.get_payment_methods()
        expenses_by_category = self.get_expenses_by_category()
        revenue_by_date = self.get_revenue_by_date()
        profit_comparison = self.get_profit_comparison()

        context.update(
            {
                "weekday_sales": self.with_percentages(weekday_sales, "total"),
                "top_products": self.with_percentages(top_products, "quantity"),
                "top_profit_products": self.with_percentages(top_profit_products, "total"),
                "payment_methods": self.with_percentages(payment_methods, "total"),
                "expenses_by_category": self.with_percentages(expenses_by_category, "total"),
                "revenue_by_date": self.with_percentages(revenue_by_date, "total"),
                "profit_comparison": self.with_percentages(profit_comparison, "total"),
                "totals": self.get_totals(profit_comparison),
            }
        )
        return context

    def get_weekday_sales(self):
        weekday_labels = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]
        sales = defaultdict(lambda: {"quantity": 0, "total": Decimal("0")})

        for item in SaleItem.objects.select_related("sale"):
            weekday = timezone.localtime(item.sale.created_at).weekday()
            sales[weekday]["quantity"] += item.quantity
            sales[weekday]["total"] += item.total_price

        return [
            {
                "label": weekday_labels[weekday],
                "quantity": values["quantity"],
                "total": values["total"],
            }
            for weekday, values in sorted(sales.items(), key=lambda item: item[1]["total"], reverse=True)
        ]

    def get_top_products_by_quantity(self):
        products = defaultdict(int)
        for item in SaleItem.objects.select_related("product"):
            products[item.product.name] += item.quantity

        return [
            {
                "label": product_name,
                "quantity": quantity,
            }
            for product_name, quantity in sorted(products.items(), key=lambda item: (-item[1], item[0]))[:5]
        ]

    def get_top_products_by_profit(self):
        products = defaultdict(lambda: Decimal("0"))
        for item in SaleItem.objects.select_related("product"):
            products[item.product.name] += (item.unit_price - item.product.cost_price) * item.quantity

        return [
            {
                "label": product_name,
                "total": profit,
            }
            for product_name, profit in sorted(products.items(), key=lambda item: (-item[1], item[0]))[:5]
        ]

    def get_payment_methods(self):
        payment_labels = dict(Sale.PAYMENT_METHOD_CHOICES)
        methods = (
            Sale.objects.values("payment_method")
            .annotate(total=Coalesce(Sum("items__quantity"), 0))
            .order_by("-total")
        )
        return [
            {
                "label": payment_labels.get(row["payment_method"], row["payment_method"]),
                "total": row["total"],
            }
            for row in methods
        ]

    def get_expenses_by_category(self):
        expenses = (
            FinancialTransaction.objects.filter(type=FinancialTransaction.EXPENSE)
            .values("category__name")
            .annotate(
                total=Coalesce(
                    Sum("amount"),
                    Decimal("0"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .order_by("-total", "category__name")[:8]
        )
        return [
            {
                "label": row["category__name"],
                "total": row["total"],
            }
            for row in expenses
        ]

    def get_revenue_by_date(self):
        revenues = (
            FinancialTransaction.objects.filter(type=FinancialTransaction.INCOME)
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(
                total=Coalesce(
                    Sum("amount"),
                    Decimal("0"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .order_by("-month")[:12]
        )
        return [
            {
                "label": row["month"].strftime("%m/%Y") if row["month"] else "Sem data",
                "total": row["total"],
            }
            for row in reversed(list(revenues))
        ]

    def get_profit_comparison(self):
        gross_profit = sum(
            (item.unit_price - item.product.cost_price) * item.quantity
            for item in SaleItem.objects.select_related("product")
        )
        expenses = FinancialTransaction.objects.aggregate(
            total=Coalesce(
                Sum("amount", filter=Q(type=FinancialTransaction.EXPENSE)),
                Decimal("0"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )["total"]
        net_profit = gross_profit - expenses
        return [
            {"label": "Lucro bruto", "total": gross_profit},
            {"label": "Lucro liquido", "total": net_profit},
        ]

    def get_totals(self, profit_comparison):
        transactions = FinancialTransaction.objects.aggregate(
            revenue=Coalesce(
                Sum("amount", filter=Q(type=FinancialTransaction.INCOME)),
                Decimal("0"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            expenses=Coalesce(
                Sum("amount", filter=Q(type=FinancialTransaction.EXPENSE)),
                Decimal("0"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
        gross_profit = profit_comparison[0]["total"] if profit_comparison else Decimal("0")
        net_profit = profit_comparison[1]["total"] if len(profit_comparison) > 1 else Decimal("0")
        return {
            "sales": Sale.objects.count(),
            "items": SaleItem.objects.aggregate(total=Coalesce(Sum("quantity"), 0))["total"],
            "revenue": transactions["revenue"],
            "expenses": transactions["expenses"],
            "gross_profit": gross_profit,
            "net_profit": net_profit,
        }

    def with_percentages(self, rows, value_key):
        if not rows:
            return []

        values = [abs(row[value_key] or 0) for row in rows]
        max_value = max(values)
        if max_value == 0:
            return [{**row, "percent": 0} for row in rows]

        return [
            {
                **row,
                "percent": int((abs(row[value_key] or 0) / max_value) * 100),
            }
            for row in rows
        ]
