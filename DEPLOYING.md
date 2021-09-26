# cycshare

cycshare is a flask based App for sharing cycling workouts. cycshare can be deployed using the `docker-compose.yml` or on a [kubernetes](https://github.com/jorgeboucas/cycshare/tree/master/kubernetes#kubernetes) cluster.

## Deploying cycshare

If you need to generate self-signed certificates you can do so by:
```
mkdir -p ~/cycshare_data/certificates 
openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -keyout ~/cycshare_data/certificates/key.pem -out ~/cycshare_data/certificates/cert.pem -subj "/C=DE/ST=NRW/L=Cologne/O=MPS/CN=cycshare"
openssl dhparam -out ~/cycshare_data/certificates/dhparam.pem 2048
```

If running cycshare on development mode make sure that you change the variable `FLASK_ENV` to `development` in `docker-compose.yml`.

Export secret variables:
```bash
cat << EOF > .env
MAIL_PASSWORD="<mail password>"
MYSQL_PASSWORD=$(openssl rand -base64 20)
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 20)
REDIS_PASSWORD=$(openssl rand -base64 20)
SECRET_KEY=$(openssl rand -base64 20)
EOF
```

or, for local development (quote all mail related entries in the `docker-compose.yml`):
```bash
cat << EOF > .env
MYSQL_PASSWORD=$(openssl rand -base64 20)
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 20)
REDIS_PASSWORD=$(openssl rand -base64 20)
SECRET_KEY=$(openssl rand -base64 20)
EOF
```

To deploy cycshare edit the `docker-compose.yml` accordingly and then:
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
If running cycshare on development mode you will have to start flask from inside the server container:
```
docker-compose exec server /bin/bash
flask run --host 0.0.0.0 --port 8000
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
docker-compose exec backup rsync -rtvh --delete /cycshare_data/users/ /backup/users_data/
```

## Looking for and removing old files

```bash
docker-compose run --entrypoint="python3 /cycshare/cycshare.py clean" init
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
from cycshare import app, db
from cycshare.models import User, UserLogging
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
docker-compose run --entrypoint="python3 /cycshare/cycshare.py stats /backup/stats" init
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
docker-compose exec mariadb /usr/bin/mysqldump -u root --password=mypass cycshare > dump.sql
```

Manually restore a database from backup:
```bash
cat dump.sql | docker-compose exec mariadb mysql --user=root --password=mypass cycshare
```

## Build and Install

```bash
python3 setup.py bdist_wheel
pip3 install cycshare-0.1.0-py3-none-any.whl
```
Static files need to be included in the `MANIFEST.in`.




