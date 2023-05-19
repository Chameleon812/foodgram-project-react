#!/bin/sh

python manage.py makemigrations

echo "Making migrations."
python manage.py migrate

echo "Loading demo data from fixtures.json"
python manage.py loaddata -i dump.json

echo "Collecting static files."
python manage.py collectstatic --noinput


exec "$@"