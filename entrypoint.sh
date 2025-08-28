#!/bin/bash
set -e
python3 manage.py shell << END
from django.contrib.auth import get_user_model

User = get_user_model()
try:
    User.objects.create_superuser("admin", "admin@example.com", "1")
except Exception as e:
    if 'auth_user_username_key' in str(e):
        ...
    else:
        print(e)
END
exec "$@"