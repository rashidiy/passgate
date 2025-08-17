from getpass import getpass

from django.core.management.base import BaseCommand

from devices.plugins import DS_K1T671MF


class Command(BaseCommand):
    help = "Custom run command with username/password"

    def add_arguments(self, parser):
        parser.add_argument("address", type=str, help="Camera device address.")
        parser.add_argument("--username", type=str)
        parser.add_argument("--password", type=str)

    def handle(self, *args, **options):
        address = options.get("address")
        username = options.get('username') or input("Username: ")
        password = options.get('password') or getpass()

        print(username, password)
        camera = DS_K1T671MF(*address.split(':'), username=username, password=password)
        camera.check_model_match()

        self.stdout.write(self.style.SUCCESS(f"Successfully connected to {address}!"))
