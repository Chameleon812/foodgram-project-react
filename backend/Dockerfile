FROM python:3.9.0 
 
WORKDIR /app 

COPY . .

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
