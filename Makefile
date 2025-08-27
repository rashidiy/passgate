mig:
	django-admin makemigrations
	django-admin migrate
admin:
	django-admin createsuperuser --email ''  --username 'admin'

po:
	django-admin makemessages --all --ignore=.venv
mo:
	django-admin compilemessages --ignore=.venv
