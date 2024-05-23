#!/bin/ash

sass --update .:.
tsc
poetry run python manage.py migrate
poetry run $@
