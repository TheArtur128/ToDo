#!/bin/ash

tsc
poetry run python manage.py migrate
poetry run $@
