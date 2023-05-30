#!/bin/sh

echo "Loading demo data."
python manage.py loaddata -i dump.json

echo "Collecting static files."
python manage.py collectstatic --noinput

gunicorn -w 2 -b 0:8000 foodgram.wsgi
