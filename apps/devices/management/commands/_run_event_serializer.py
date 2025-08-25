import os

import django


def main():
    from devices.management.commands.event_listener import Command
    Command().handle()


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
    django.setup()
    main()
