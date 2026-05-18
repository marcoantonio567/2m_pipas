from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection, transaction

from app.models import Client, FinancialCategory, FinancialTransaction, Product, Sale, SaleItem


class Command(BaseCommand):
    help = "Remove todos os dados da aplicacao, mantendo a estrutura do banco e as migracoes."

    APP_MODELS = [
        SaleItem,
        FinancialTransaction,
        Sale,
        Product,
        Client,
        FinancialCategory,
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Confirma a limpeza sem pedir interacao no terminal.",
        )
        parser.add_argument(
            "--keep-sale-category",
            action="store_true",
            help="Mantem ou recria a categoria financeira protegida 'venda'.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["yes"] and not self.confirm_cleanup():
            self.stdout.write(self.style.WARNING("Limpeza cancelada."))
            return

        deleted_counts = self.delete_app_data()
        self.reset_sequences()

        if options["keep_sale_category"]:
            FinancialCategory.objects.get_or_create(name=FinancialCategory.PROTECTED_NAME)

        self.print_summary(deleted_counts, options["keep_sale_category"])

    def confirm_cleanup(self):
        database_name = connection.settings_dict.get("NAME")
        self.stdout.write(
            self.style.WARNING(
                "Isso vai apagar clientes, produtos, vendas, itens de venda, "
                "categorias financeiras e movimentacoes financeiras."
            )
        )
        self.stdout.write(f"Banco alvo: {database_name}")
        answer = input("Digite LIMPAR para confirmar: ")
        return answer == "LIMPAR"

    def delete_app_data(self):
        deleted_counts = {}

        for model in self.APP_MODELS:
            deleted, details = model.objects.all().delete()
            deleted_counts[model.__name__] = details.get(model._meta.label, deleted)

        return deleted_counts

    def reset_sequences(self):
        sql_statements = connection.ops.sequence_reset_sql(no_style(), self.APP_MODELS)
        if not sql_statements:
            return

        with connection.cursor() as cursor:
            for sql in sql_statements:
                cursor.execute(sql)

    def print_summary(self, deleted_counts, kept_sale_category):
        labels = {
            "SaleItem": "itens de venda",
            "FinancialTransaction": "movimentacoes financeiras",
            "Sale": "vendas",
            "Product": "produtos",
            "Client": "clientes",
            "FinancialCategory": "categorias financeiras",
        }

        self.stdout.write(self.style.SUCCESS("Banco limpo com sucesso."))
        for model_name, count in deleted_counts.items():
            self.stdout.write(f"- {labels[model_name]}: {count}")

        if kept_sale_category:
            self.stdout.write("- categoria protegida 'venda': mantida/recriada")
