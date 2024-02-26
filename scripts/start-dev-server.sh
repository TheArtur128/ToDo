#!/bin/ash

poetry run python manage.py migrate
rm static -fr
poetry run python manage.py collectstatic 
poetry run python manage.py runserver
