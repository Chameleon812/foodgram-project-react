#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset

if [ "$POSTGRES_USER" = "postgres" ]; then
    echo "Waiting for PostgreSQL to become available..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL is available"
fi


python manage.py makemigrations

echo "Making migrations."
python manage.py migrate

echo "Loading demo data from fixtures.json"
python manage.py loaddata -i dump.json

echo "Collecting static files."
python manage.py collectstatic --noinput


exec "$@"