# myapp

myapp is a universal backbone for flask-dash based apps with user level authentication. flaskapp can be deployed using the `docker-compose.yml` or on a [kubernetes](https://github.com/jorgeboucas/myapp/tree/master/kubernetes#kubernetes) cluster.

## Deploying myapp

Start by defining your apps folder name 
```
export APP_NAME="myapp"
```
as seen in the base folder of this repo.

If you need to generate self-signed certificates you can do so by:
```
mkdir -p ~/${APP_NAME}_data/certificates 
openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -keyout ~/${APP_NAME}_data/certificates/key.pem -out ~/${APP_NAME}_data/certificates/cert.pem -subj "/C=DE/ST=NRW/L=Cologne/O=MPS/CN=${APP_NAME}"
openssl dhparam -out ~/${APP_NAME}_data/certificates/dhparam.pem 2048
```

On a Mac double click on the cert.pem file to open it and add it to the Keychain. In key chain double click on the certificate to change Trust : When using this certificate : Always trust. 

If running myapp on development mode make sure that you change the variable `FLASK_ENV` to `development` in `docker-compose.yml`.

For production export secret variables into `.env.prod`:
```bash
cat << EOF > .env.prod
APP_NAME="${APP_NAME}"
MAIL_PASSWORD="<mail password>"
MYSQL_PASSWORD=$(openssl rand -base64 20)
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 20)
REDIS_PASSWORD=$(openssl rand -base64 20)
SECRET_KEY=$(openssl rand -base64 20)
EOF
```

and specify the env file when starting container eg. `docker-compose --env-file .env.prod up`.

For local development (quote all mail related entries in the `docker-compose.yml`):
```bash
cat << EOF > .env
APP_NAME="${APP_NAME}"
MYSQL_PASSWORD=$(openssl rand -base64 20)
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 20)
REDIS_PASSWORD=$(openssl rand -base64 20)
SECRET_KEY=$(openssl rand -base64 20)
EOF
```

Create local folders:

```
mkdir -p ~/myapp_backup/stats ~/myapp_backup/users_data ~/myapp_backup/mariadb
```

To deploy myapp edit the `docker-compose.yml` accordingly and then:
```bash
docker-compose up -d --build
```
Check the `stdout` with:
```bash
docker-compose logs
```
or for example:
```bash
docker-compose logs -f server
```
If running myapp on development mode you will have to start flask from inside the server container:
```
docker-compose exec server /bin/bash
flask run --host 0.0.0.0 --port 8000
docker-compose up -d --build && docker-compose exec server flask run --host 0.0.0.0 --port 8000

```
Adding administrator user:
```
docker-compose run --entrypoint="python3 /myapp/myapp.py admin --add myemail@gmail.com" init 
```

You can connect to any of the running containers by eg. 
```bash
docker-compose exec mariadb /bin/bash
```
For stopping and removing a container,
```bash
docker-compose stop mariadb && docker-compose rm mariadb
```
Stopping and removing all containers:
```bash
docker-compose down
```
Stopping and removing all containers as well as all volumes (this will destroy the volumes and contained data):
```bash
docker-compose down -v
```
To remove a volume, eg.
```bash
docker volume rm db
```

## Backups

```bash
docker-compose exec backup /backup.sh
docker-compose exec backup rsync -rtvh --delete /${APP_NAME}_data/users/ /backup/users_data/
```

## Email logging

To use the SMTP debugging server from Python comment all email related `env` in `docker-compose.yml`.
You can not using python's fake email server that accepts emails, but instead of sending them, it prints them to the console. 
To run this server, open a second terminal session and run the following command on it:
```bash
docker-compose exec server python3 -m smtpd -n -c DebuggingServer localhost:8025
```

## Databases

For handling database entries you can start the `flask shell` by:
```bash
docker-compose exec server flask shell 
```
make the required imports:
```python
from myapp import app, db
from myapp.models import User, UserLogging
```
and then for removing a user from the db:
```python
u=User.query.filter_by(email=<user_email>).first()
db.session.delete(u)
db.session.commit()
```
for editing entries eg.:
```python
user=User.query.filter_by(email=<user_email>).first()
user.active = False
db.session.add(user)
db.session.commit()
```

Collecting usage entries:
```bash
docker-compose run --entrypoint="python3 /${APP_NAME}/${APP_NAME}.py stats /backup/stats" init
```

If you need to re-initiate your database
```bash
rm -rf migrations && flask db init && flask db migrate -m "users table" && flask db upgrade 
```

upgrading
```bash
flask db migrate -m "new fields in user model"
flask db upgrade
```

Manually backup a database:
```bash
docker-compose exec mariadb /usr/bin/mysqldump -u root --password=mypass ${APP_NAME} > dump.sql
```

Manually restore a database from backup:
```bash
cat dump.sql | docker-compose exec mariadb mysql --user=root --password=mypass ${APP_NAME}
```

## Multiplatform builds

Builds are currently working for `linux/amd64` and `linux/arm64` but not for `linux/arm/v7`.

```
docker buildx create --name mybuilder
docker buildx use mybuilder
docker buildx inspect --bootstrap
docker buildx build --platform linux/amd64,linux/arm64 --build-arg BUILD_NAME=myapp --no-cache --force-rm -t myapp/myapp:latest -f services/server/Dockerfile . --load
```

To push result image into registry use --push or to load image into docker use --load.
