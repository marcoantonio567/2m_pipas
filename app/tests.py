from django.test import TestCase
from django.urls import reverse

from .models import Client, FinancialCategory, FinancialTransaction, Product, Sale, SaleItem


class ClientTests(TestCase):
    def test_client_search_ignores_accents_and_case(self):
        Client.objects.create(name="Joao Pedro", age="20")
        Client.objects.create(name="João Silva", age="30")
        Client.objects.create(name="Maria", age="25")

        response = self.client.get(reverse("clientes"), {"q": "joão"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Joao Pedro")
        self.assertContains(response, "João Silva")
        self.assertNotContains(response, "Maria")

        response = self.client.get(reverse("clientes"), {"q": "Joao"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Joao Pedro")
        self.assertContains(response, "João Silva")
        self.assertNotContains(response, "Maria")


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

    def test_financial_transaction_can_be_deleted(self):
        category = FinancialCategory.objects.get(name="venda")
        transaction = FinancialTransaction.objects.create(
            type=FinancialTransaction.EXPENSE,
            category=category,
            description="Compra",
            amount="15.00",
            date="2026-05-13",
        )

        response = self.client.post(
            reverse("financeiro_movimentacao_excluir", args=[transaction.id])
        )

        self.assertRedirects(response, reverse("financeiro_caixa"))
        self.assertFalse(FinancialTransaction.objects.filter(id=transaction.id).exists())


class SaleTests(TestCase):
    def test_sale_create_registers_new_client_payment_financial_entry_and_stock(self):
        product = Product.objects.create(
            name="Pipa colorida",
            description="Pipa pronta",
            quantity=5,
            cost_price="4.00",
            price="10.00",
        )

        response = self.client.post(
            reverse("venda_nova"),
            {
                "product": product.id,
                "quantity": 2,
                "client_name": "Maria",
                "payment_method": Sale.CARD,
            },
        )

        self.assertRedirects(response, reverse("vendas"))
        client = Client.objects.get(name="Maria")
        sale = Sale.objects.get(client=client)
        sale_item = SaleItem.objects.get(sale=sale)
        product.refresh_from_db()

        self.assertEqual(sale.payment_method, Sale.CARD)
        self.assertEqual(sale_item.product, product)
        self.assertEqual(sale_item.quantity, 2)
        self.assertEqual(sale_item.unit_price, product.price)
        self.assertEqual(product.quantity, 3)
        self.assertTrue(
            FinancialTransaction.objects.filter(
                type=FinancialTransaction.INCOME,
                category__name=FinancialCategory.PROTECTED_NAME,
                amount="20.00",
                description__contains="Cartao",
            ).exists()
        )

    def test_sale_create_uses_existing_client_when_selected(self):
        client = Client.objects.create(name="Joao", age="30")
        product = Product.objects.create(
            name="Linha",
            description="Linha resistente",
            quantity=3,
            cost_price="2.00",
            price="7.50",
        )

        response = self.client.post(
            reverse("venda_nova"),
            {
                "product": product.id,
                "quantity": 1,
                "client_name": "Joao",
                "payment_method": Sale.PIX,
            },
        )

        self.assertRedirects(response, reverse("vendas"))
        self.assertEqual(Client.objects.count(), 1)
        self.assertTrue(Sale.objects.filter(client=client, payment_method=Sale.PIX).exists())

    def test_sale_can_be_deleted_and_restores_stock_and_financial_entry(self):
        client = Client.objects.create(name="Ana", age="28")
        category = FinancialCategory.objects.get(name="venda")
        product = Product.objects.create(
            name="Rabiola",
            description="Rabiola colorida",
            quantity=2,
            cost_price="1.00",
            price="5.00",
        )
        sale = Sale.objects.create(client=client, payment_method=Sale.CASH)
        SaleItem.objects.create(sale=sale, product=product, quantity=3, unit_price="5.00")
        FinancialTransaction.objects.create(
            type=FinancialTransaction.INCOME,
            category=category,
            description=f"Venda #{sale.id} - Ana - Dinheiro",
            amount="15.00",
            date="2026-05-13",
        )

        response = self.client.post(reverse("venda_excluir", args=[sale.id]))

        self.assertRedirects(response, reverse("vendas"))
        product.refresh_from_db()
        self.assertEqual(product.quantity, 5)
        self.assertFalse(Sale.objects.filter(id=sale.id).exists())
        self.assertFalse(FinancialTransaction.objects.filter(description__startswith=f"Venda #{sale.id} -").exists())
