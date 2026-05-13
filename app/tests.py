from django.test import TestCase
from django.urls import reverse

from .models import FinancialCategory, FinancialTransaction


class FinancialCategoryTests(TestCase):
    def test_financial_category_list_creates_default_sale_category(self):
        response = self.client.get(reverse("financeiro_categorias"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(FinancialCategory.objects.filter(name="venda").exists())

    def test_default_sale_category_cannot_be_updated(self):
        category = FinancialCategory.objects.get(name="venda")

        response = self.client.post(
            reverse("financeiro_categoria_alterar", args=[category.id]),
            {"name": "outra"},
        )

        category.refresh_from_db()
        self.assertRedirects(response, reverse("financeiro_categorias"))
        self.assertEqual(category.name, "venda")

    def test_default_sale_category_cannot_be_deleted(self):
        category = FinancialCategory.objects.get(name="venda")

        response = self.client.post(reverse("financeiro_categoria_excluir", args=[category.id]))

        self.assertRedirects(response, reverse("financeiro_categorias"))
        self.assertTrue(FinancialCategory.objects.filter(id=category.id).exists())

    def test_financial_transaction_requires_category(self):
        response = self.client.post(
            reverse("financeiro_movimentacao_nova"),
            {
                "type": FinancialTransaction.INCOME,
                "description": "Entrada sem categoria",
                "amount": "10.00",
                "date": "2026-05-13",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(FinancialTransaction.objects.exists())

    def test_cash_register_shows_income_expense_and_balance(self):
        category = FinancialCategory.objects.get(name="venda")
        FinancialTransaction.objects.create(
            type=FinancialTransaction.INCOME,
            category=category,
            description="Venda",
            amount="100.00",
            date="2026-05-13",
        )
        FinancialTransaction.objects.create(
            type=FinancialTransaction.EXPENSE,
            category=category,
            description="Compra",
            amount="35.50",
            date="2026-05-13",
        )

        response = self.client.get(reverse("financeiro_caixa"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "R$ 100.00")
        self.assertContains(response, "R$ 35.50")
        self.assertContains(response, "R$ 64.50")
