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

# from werkzeug import wsgi
# import werkzeug

# from werkzeug.middleware.dispatcher import ProxyMiddleware

from myapp.routes._vars import _PRIVATE_ROUTES, _PUBLIC_VIEWS

PRIVATE_ROUTES=[ ] + _PRIVATE_ROUTES
PUBLIC_VIEWS=[ ] + _PUBLIC_VIEWS

app = Flask(__name__)
app.config.from_object(Config)

# class PrefixMiddleware(object):

#     def __init__(self, app, prefix=''):
#         self.app = app
#         self.prefix = prefix

#     def __call__(self, environ, start_response):

#         if environ['PATH_INFO'].startswith(self.prefix):
#             environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
#             environ['SCRIPT_NAME'] = self.prefix
#             return self.app(environ, start_response)
#         else:
#             start_response('404', [('Content-Type', 'text/plain')])
#             return ["This url does not belong to the app.".encode()]

# app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/v3')

# app = werkzeug.wsgi.ProxyMiddleware(app, {
#     '/v3': {
#         'remove_prefix':True
#         # 'target': 'http://127.0.0.1:5001/',
#     }
# })

# from werkzeug.middleware.dispatcher import DispatcherMiddleware
# from werkzeug.wrappers import Response

# app.wsgi_app = DispatcherMiddleware(
#     app,
#     {'/v3': app.wsgi_app}
# )

# def prefix_route(route_function, prefix='', mask='{0}{1}'):
#   '''
#     Defines a new route function with a prefix.
#     The mask argument is a `format string` formatted with, in that order:
#       prefix, route
#   '''
#   def newroute(route, *args, **kwargs):
#     '''New function to prefix the route'''
#     return route_function(mask.format(prefix, route), *args, **kwargs)
#   return newroute
# app.route = prefix_route(app.route, '/v3')
# app.config['APPLICATION_ROOT'] = '/v3'

db = SQLAlchemy(app ,engine_options={"pool_pre_ping":True, "pool_size":0,"pool_recycle":-1} )
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = '/login/'
mail = Mail(app)
sess = Session()
sess.init_app(app)

# from werkzeug.wsgi import DispatcherMiddleware
# app.wsgi_app = DispatcherMiddleware(
#     app,
#     {'/v3': app.wsgi_app},
# )


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