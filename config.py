import os
import secrets
import redis

basedir = os.path.abspath(os.path.dirname(__file__))

if os.path.isfile(basedir+"/.git/refs/heads/master" ):
    with open(basedir+"/.git/refs/heads/master", "r") as f:
        commit=f.readline().split("\n")[0]
else:
    with open(basedir+"/.git/refs/heads/main", "r") as f:
        commit=f.readline().split("\n")[0]

class Config(object):
    MYAPP_VERSION=os.environ.get('MYAPP_VERSION') or "none"
    APP_VERSION=os.environ.get('APP_VERSION') or "none"
    APP_NAME=os.environ.get('APP_NAME') or "myapp"
    APP_TITLE=os.environ.get('APP_TITLE') or "myapp"
    APP_URL=os.environ.get('APP_URL')  or 'https://0.0.0.0'
    APP_ASSETS=os.environ.get('APP_ASSETS') or f'/{APP_NAME}/{APP_NAME}/static/'
    USERS_DATA = os.environ.get('USERS_DATA') or "/myapp/users/"
    LOGS = os.environ.get('LOGS') or '/var/log/myapp/'
    session_token=secrets.token_urlsafe(16)
    SECRET_KEY = os.environ.get('SECRET_KEY') or session_token
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_TYPE = os.environ.get('SESSION_TYPE') or 'redis'
    redis_password = os.environ.get('REDIS_PASSWORD') or 'REDIS_PASSWORD'
    REDIS_ADDRESS = os.environ.get('REDIS_ADDRESS') or '127.0.0.1:6379/0'
    SESSION_REDIS = redis.from_url('redis://:%s@%s' %(redis_password,REDIS_ADDRESS))
    MYSQL_USER = os.environ.get('MYSQL_USER') or APP_NAME
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'mypass'
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'mariadb'
    MYSQL_PORT = os.environ.get('MYSQL_PORT') or '3306'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s' %(MYSQL_USER,MYSQL_PASSWORD,MYSQL_HOST,MYSQL_PORT,APP_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 8025)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    INSTANCE = os.environ.get('INSTANCE') or "PRODUCTION"
    COMMIT = commit
    ADMINS = os.environ.get('ADMINS').split(",") or ['jboucas@gmail.com']
    # PRIVATE_APPS = os.environ.get('PRIVATE_APPS') or None


