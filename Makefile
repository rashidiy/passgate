mig:
	python3 manage.py makemigrations
	python3 manage.py migrate
admin:
	python3 manage.py createsuperuser --email ''  --username 'admin'

po:
	python3 manage.py makemessages --all
mo:
	python3 manage.py compilemessages --ignore=.venv
