import random
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from app.models import Client, FinancialCategory, FinancialTransaction, Product, Sale, SaleItem


class Command(BaseCommand):
    help = "Cria dados ficticios para visualizar o sistema com vendas, produtos e financeiro."

    CLIENTS = [
        ("Ana Souza", "24"),
        ("Bruno Lima", "31"),
        ("Carla Mendes", "28"),
        ("Diego Rocha", "35"),
        ("Eduarda Nunes", "22"),
        ("Felipe Martins", "39"),
        ("Gabriela Costa", "27"),
        ("Henrique Alves", "41"),
        ("Isabela Ribeiro", "19"),
        ("Joao Pedro", "33"),
        ("Karina Lopes", "26"),
        ("Lucas Ferreira", "30"),
        ("Mariana Gomes", "37"),
        ("Nicolas Vieira", "21"),
        ("Otavio Santos", "44"),
        ("Patricia Barros", "32"),
        ("Rafael Teixeira", "29"),
        ("Sofia Cardoso", "18"),
        ("Thiago Moreira", "36"),
        ("Valentina Dias", "25"),
    ]

    PRODUCTS = [
        ("Pipa Brasil 60cm", "Pipa tradicional com estampa do Brasil.", 145, "3.80", "9.90"),
        ("Pipa Dragao", "Modelo colorido com rabiola reforcada.", 118, "4.50", "12.90"),
        ("Pipa Neon", "Pipa de seda neon para alta visibilidade.", 132, "5.20", "14.90"),
        ("Pipa Tubarao", "Modelo infantil com desenho de tubarao.", 96, "4.10", "11.90"),
        ("Pipa Foguete", "Pipa leve para vento fraco.", 106, "3.60", "10.90"),
        ("Pipa Aguia", "Pipa premium com vareta de bambu.", 82, "6.40", "18.90"),
        ("Pipa Arraia", "Formato classico com papel resistente.", 124, "3.90", "10.50"),
        ("Pipa Caveira", "Estampa radical para colecionadores.", 75, "5.10", "15.50"),
        ("Linha 500 jardas", "Linha branca para pipas.", 170, "4.80", "12.00"),
        ("Linha chilena colorida", "Linha colorida para uso recreativo.", 88, "7.50", "19.90"),
        ("Carretel simples", "Carretel plastico leve.", 135, "2.70", "7.90"),
        ("Carretel reforcado", "Carretel maior com pegada firme.", 72, "6.80", "17.90"),
        ("Rabiola colorida", "Rabiola pronta em cores variadas.", 210, "1.20", "4.50"),
        ("Vareta bambu pacote", "Pacote com varetas para manutencao.", 160, "2.10", "6.90"),
        ("Kit Pipa Infantil", "Kit com pipa, linha e rabiola.", 64, "9.80", "29.90"),
    ]

    EXPENSE_CATEGORIES = [
        "aluguel",
        "energia",
        "internet",
        "fornecedores",
        "marketing",
        "embalagens",
        "manutencao",
        "transporte",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-mock",
            action="store_true",
            help="Remove dados ficticios criados por este comando antes de popular novamente.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)

        if options["reset_mock"]:
            self.reset_mock_data()

        clients = self.create_clients()
        products = self.create_products()
        categories = self.create_categories()
        sales_created = self.create_sales(clients, products)
        expenses_created = self.create_expenses(categories)

        self.stdout.write(
            self.style.SUCCESS(
                "Dados ficticios criados: "
                f"{len(clients)} clientes, {len(products)} produtos, "
                f"{sales_created} vendas e {expenses_created} saidas financeiras."
            )
        )

    def reset_mock_data(self):
        mock_client_names = [name for name, _age in self.CLIENTS]
        mock_product_names = [name for name, *_rest in self.PRODUCTS]
        mock_category_names = self.EXPENSE_CATEGORIES + [FinancialCategory.PROTECTED_NAME]

        Sale.objects.filter(client__name__in=mock_client_names).delete()
        FinancialTransaction.objects.filter(description__startswith="[MOCK]").delete()
        Product.objects.filter(name__in=mock_product_names).delete()
        Client.objects.filter(name__in=mock_client_names).delete()
        FinancialCategory.objects.filter(name__in=mock_category_names).exclude(
            name=FinancialCategory.PROTECTED_NAME
        ).delete()

    def create_clients(self):
        clients = []
        for name, age in self.CLIENTS:
            client, _created = Client.objects.get_or_create(
                name=name,
                defaults={"age": age},
            )
            if client.age != age:
                client.age = age
                client.save(update_fields=["age"])
            clients.append(client)
        return clients

    def create_products(self):
        products = []
        for name, description, quantity, cost_price, price in self.PRODUCTS:
            product, _created = Product.objects.update_or_create(
                name=name,
                defaults={
                    "description": description,
                    "quantity": quantity,
                    "cost_price": Decimal(cost_price),
                    "price": Decimal(price),
                },
            )
            products.append(product)
        return products

    def create_categories(self):
        categories = {}
        for name in self.EXPENSE_CATEGORIES:
            categories[name], _created = FinancialCategory.objects.get_or_create(name=name)
        FinancialCategory.objects.get_or_create(name=FinancialCategory.PROTECTED_NAME)
        return categories

    def create_sales(self, clients, products):
        sales_category, _created = FinancialCategory.objects.get_or_create(
            name=FinancialCategory.PROTECTED_NAME
        )
        created = 0
        today = timezone.localdate()
        payment_methods = [Sale.PIX, Sale.CASH, Sale.CARD]
        product_weights = [14, 13, 12, 10, 9, 8, 7, 7, 6, 5, 5, 4, 4, 3, 3]

        for index in range(95):
            client = random.choice(clients)
            sale_date = today - timedelta(days=random.randint(0, 44))
            sale_time = time(
                hour=random.randint(8, 20),
                minute=random.choice([0, 5, 10, 15, 20, 30, 40, 45, 50]),
            )
            sale_datetime = timezone.make_aware(datetime.combine(sale_date, sale_time))
            sale = Sale.objects.create(
                client=client,
                payment_method=random.choice(payment_methods),
            )
            Sale.objects.filter(pk=sale.pk).update(created_at=sale_datetime)

            total = Decimal("0")
            selected_products = random.choices(products, weights=product_weights, k=random.randint(1, 3))
            for product in dict.fromkeys(selected_products):
                quantity = random.randint(1, 4)
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price,
                )
                product.quantity = max(product.quantity - quantity, 0)
                product.save(update_fields=["quantity"])
                total += product.price * quantity

            FinancialTransaction.objects.create(
                type=FinancialTransaction.INCOME,
                category=sales_category,
                description=f"[MOCK] Venda #{sale.id} - {client.name} - {sale.get_payment_method_display()}",
                amount=total,
                date=sale_date,
            )
            created += 1

        return created

    def create_expenses(self, categories):
        created = 0
        today = timezone.localdate()
        expense_templates = [
            ("aluguel", "Aluguel da loja", "950.00", "1250.00"),
            ("energia", "Conta de energia", "120.00", "330.00"),
            ("internet", "Internet e telefone", "90.00", "180.00"),
            ("fornecedores", "Compra de mercadorias", "480.00", "1450.00"),
            ("marketing", "Anuncios e divulgacao", "80.00", "260.00"),
            ("embalagens", "Sacolas e etiquetas", "45.00", "190.00"),
            ("manutencao", "Manutencao da loja", "70.00", "310.00"),
            ("transporte", "Fretes e entregas", "60.00", "240.00"),
        ]

        for index in range(42):
            category_name, label, min_value, max_value = random.choice(expense_templates)
            amount = Decimal(random.uniform(float(min_value), float(max_value))).quantize(Decimal("0.01"))
            expense_date = today - timedelta(days=random.randint(0, 44))
            FinancialTransaction.objects.create(
                type=FinancialTransaction.EXPENSE,
                category=categories[category_name],
                description=f"[MOCK] {label}",
                amount=amount,
                date=expense_date,
            )
            created += 1

        return created
