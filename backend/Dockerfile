FROM python:3.9.0 
 
WORKDIR /app 

COPY . .

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

ADD django_entrypoint.sh /django_entrypoint.sh

RUN chmod a+x /django_entrypoint.sh

ENTRYPOINT ["/django_entrypoint.sh"]
