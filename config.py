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
    USERS_DATA = os.environ.get('USERS_DATA') or f'/{APP_NAME}_data/users'
    LOGS = os.environ.get('LOGS') or '/var/log/myapp/'
    session_token=secrets.token_urlsafe(16)
    SECRET_KEY = os.environ.get('SECRET_KEY') or session_token
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_TYPE = 'redis' #'redis'
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'RedisCache' # or RedisSentinelCache
    CACHE_REDIS_SENTINELS = [ [ os.environ.get('CACHE_REDIS_SENTINELS_address') or None ,  os.environ.get('CACHE_REDIS_SENTINELS_port') or None ] ]
    CACHE_REDIS_SENTINEL_MASTER = os.environ.get('CACHE_REDIS_SENTINEL_MASTER') or None
    CACHE_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD') or 'REDIS_PASSWORD'
    MYSQL_USER = os.environ.get('MYSQL_USER') or APP_NAME
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'mypass'
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'mariadb'
    MYSQL_PORT = os.environ.get('MYSQL_PORT') or '3306'
    DB_NAME = os.environ.get('DB_NAME') or 'myapp'
    PAGE_PREFIX = os.environ.get('PAGE_PREFIX') or ""
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s' %(MYSQL_USER,MYSQL_PASSWORD,MYSQL_HOST,MYSQL_PORT,DB_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 8025)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # print("MAIL PASSWORD", MAIL_PASSWORD)
    INSTANCE = os.environ.get('INSTANCE') or "PRODUCTION"
    COMMIT = commit
    ADMINS = os.environ.get('ADMINS').split(",") or ['jboucas@gmail.com']
    PREAUTH = os.environ.get('PREAUTH') or True

    # PRIVATE_APPS = os.environ.get('PRIVATE_APPS') or None


