#!/usr/bin/env python
import os
import sys

# # Debug uchun
# def print_env_details():
#     env_path = Path(__file__).resolve().parent / '.env'
#     print(f"1. .env file path: {env_path}")
#     print(f"2. .env exists: {os.path.exists(env_path)}")
#
#     # .env faylini to'g'ridan-to'g'ri o'qish
#     if os.path.exists(env_path):
#         with open(env_path, 'r') as f:
#             print("3. .env content:")
#             print(f.read())
#
#     # Environment o'zgaruvchilarini tekshirish
#     print("\n4. Environment variables:")
#     print(f"CAM_IP (before load_dotenv): {os.getenv('CAM_IP')}")
#
#     # .env ni yuklash
#     load_dotenv(env_path)
#     print(f"CAM_IP (after load_dotenv): {os.getenv('CAM_IP')}")
#
# print_env_details()


from orders.plugins.DS_K1T671MF.camera import switch_cam


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    switch_cam(False)
    main()
