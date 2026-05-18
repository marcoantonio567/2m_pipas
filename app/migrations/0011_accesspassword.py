from django.db import migrations, models


def create_default_access_password(apps, schema_editor):
    AccessPassword = apps.get_model("app", "AccessPassword")
    AccessPassword.objects.update_or_create(
        password="162636",
        defaults={"is_active": True},
    )


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0010_product_line_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccessPassword",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RunPython(create_default_access_password, migrations.RunPython.noop),
    ]
