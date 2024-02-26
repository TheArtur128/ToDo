#!/bin/ash

rm static -fr
tsc
poetry run python manage.py migrate
poetry run python manage.py collectstatic
poetry run $@
