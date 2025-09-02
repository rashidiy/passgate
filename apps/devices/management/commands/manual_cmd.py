from django.core.management import BaseCommand
from django.db import connection

from devices.models import Device, Event


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--execute', nargs='+', metavar='cmd_<command_name>')

    def cmd_skip_event_history(self):
        Device.objects.filter(ip_address='192.168.10.215').update(last_event=39431)
        Device.objects.filter(ip_address='192.168.10.216').update(last_event=37589)
        with connection.cursor() as cursor:
            cursor.execute(f'TRUNCATE TABLE {Event._meta.db_table} RESTART IDENTITY CASCADE')

    def handle(self, *args, **options):
        """
        As long as you try to create manual_commands you should have to register them as attribute of class Command.
        Attribute has to start with cmd_<method_name>
        """
        executers = options.get('execute')
        for cmd in executers:
            if cmd.startswith('cmd_'):
                if attr := getattr(self, cmd, None):
                    attr()
