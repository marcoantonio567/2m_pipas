from django.db import migrations


def create_default_financial_category(apps, schema_editor):
    FinancialCategory = apps.get_model("app", "FinancialCategory")
    FinancialCategory.objects.get_or_create(name="venda")


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_financialcategory"),
    ]

    operations = [
        migrations.RunPython(create_default_financial_category, migrations.RunPython.noop),
    ]
