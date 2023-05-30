FROM python:3.9.0

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

RUN echo "Loading demo data." \
    && python manage.py loaddata -i dump.json \
    && echo "Collecting static files." \
    && python manage.py collectstatic --noinput

CMD gunicorn -w 2 -b 0:8000 foodgram.wsgi