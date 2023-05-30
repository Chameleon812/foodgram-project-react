FROM python:3.9.0 
 
WORKDIR /app 

COPY . .

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

RUN echo "Loading demo data." \
    && python manage.py loaddata -i dump.json \
    && echo "Collecting static files." \
    && python manage.py collectstatic --noinput

CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
