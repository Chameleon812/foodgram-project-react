# Foodgram-project
Service for publishing and sharing recipes.

Authorized users can subscribe to authors they like, add recipes to favorites, to purchases, and download a shopping list. Unauthorized users have access to registration, authorization, and viewing recipes of other users.


## Technology stack
Python 3.9, Django 4.2, Django REST Framework 3.14, PostgresQL, Docker, Yandex.Cloud.

## Installation
To run locally, create a `.env` file in the `/backend/` directory with the following content:
```
SECRET_KEY=any_secret_key_of_your_choice
DEBUG=False
ALLOWED_HOSTS=*, or your hosts
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password_for_database_of_your_choice
DB_HOST=bd
DB_PORT=5432
```
#### Installing Docker

To run the project you will need to install Docker and docker-compose.

To install on ubuntu run the following commands:

```bash
sudo apt install docker docker-compose
```


### Installing the project on the server
1. Copy the files from the `/infra/` folder to your server and the `.env` file from the `/backend/` directory:
```bash
scp -r data/ <username>@<server_ip>:/home/<username>/
scp backend/.env <username>@<server_ip>:/home/<username>/
```
2. Login to the server and configure `server_name` in the nginx config to your domain name:
```bash
vim nginx.conf
```

### Project setup
1. Run docker compose:
```bash
docker-compose up -d
```
2. Apply migrations:
```bash
docker-compose exec backend python manage.py migrate
```
3. Fill the database with initial data (optional):
```bash
docker-compose exec backend python manange.py loaddata -i dump.json

```
4. Create an administrator:
```bash
docker-compose exec backend python manage.py createsuperuser
```

## API Documentation
To open the documentation locally, start the server and follow the link:
[http://127.0.0.1/api/docs/](http://127.0.0.1/api/docs/)


The project is running on the server http://158.160.111.124/
Admin login: admin@gmail.com
Admin password: 987654321!
