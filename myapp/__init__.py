import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask, redirect, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from flask_mail import Mail
from flask_session import Session
from waitress import serve

from myapp.routes._vars import _PRIVATE_ROUTES, _PUBLIC_VIEWS

PRIVATE_ROUTES=[ ] + _PRIVATE_ROUTES
PUBLIC_VIEWS=[ ] + _PUBLIC_VIEWS

app = Flask(__name__)
app.config.from_object(Config)
# if app.config["CACHE_TYPE"] == "RedisCache" :
#     print(app.config)
#     del(app.config["CACHE_REDIS_SENTINELS_address"])
#     del(app.config["CACHE_REDIS_SENTINELS_port"])
#     del(app.config["CACHE_REDIS_PASSWORD"])
# elif app.config["CACHE_TYPE"] == "RedisSentinelCache" :
#     del(app.config["REDIS_ADDRESS"])
#     del(app.config["SESSION_REDIS"])

db = SQLAlchemy(app ,engine_options={"pool_pre_ping":True, "pool_size":0,"pool_recycle":-1} )
migrate = Migrate(app, db)
PAGE_PREFIX=app.config["PAGE_PREFIX"]
login_manager = LoginManager(app)
login_manager.login_view = f'{PAGE_PREFIX}/login/'
mail = Mail(app)
sess = Session()
sess.init_app(app)


from myapp import models, errors
from myapp.routes import index, register, home, login, forgot, logout, contact, about, privacy, impressum, admin, settings
from myapp.routes._routes import *
 
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['ADMINS'][0],
            toaddrs=app.config['ADMINS'], subject=f'{app.config["INSTANCE"]} :: {app.config["APP_TITLE"]} Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists(app.config['LOGS']):
        os.mkdir(app.config['LOGS'])
    file_handler = RotatingFileHandler(app.config['LOGS']+f'{app.config["APP_NAME"]}.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info(f'{app.config["APP_NAME"]} startup')


# if __name__ == "__main__":
#    #app.run() ##Replaced with below code to run it using waitress 
#    serve(app, host='0.0.0.0', port=8000)