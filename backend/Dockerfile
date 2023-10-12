FROM python:3.9.0 
 
WORKDIR /code

COPY . /code

RUN pip install --upgrade pip && pip install -r requirements.txt
RUN python manage.py collectstatic

CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
