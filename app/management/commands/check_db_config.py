from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Prints the resolved database connection config without secrets."

    def handle(self, *args, **options):
        database = settings.DATABASES["default"]
        self.stdout.write(f"ENGINE={database.get('ENGINE', '')}")
        self.stdout.write(f"HOST={database.get('HOST', '')}")
        self.stdout.write(f"PORT={database.get('PORT', '')}")
        self.stdout.write(f"NAME={database.get('NAME', '')}")
        self.stdout.write(f"USER={database.get('USER', '')}")
        self.stdout.write(f"PASSWORD_SET={bool(database.get('PASSWORD'))}")
        self.stdout.write(f"SSLMODE={database.get('OPTIONS', {}).get('sslmode', '')}")
