from django.test import TestCase
from django.urls import reverse

from .models import FinancialCategory


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
