from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flaskapp import app, db, login_manager
from flask_login import UserMixin
from time import time
import jwt
from sqlalchemy.types import PickleType
from flask import request

PRIVATE_ROUTES=['about']
PUBLIC_VIEWS=[ 'about']

class PrivateRoutes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route = db.Column(db.String(64), index=True,unique=True)
    users = db.Column(PickleType, index=True, unique=False)
    users_domains = db.Column(PickleType, index=True, unique=False)

    # viewers_ids = db.Column(PickleType, index=True, unique=False)
    # users_domains = db.Column(PickleType, index=True, unique=False)
    # viewers_domains = db.Column(PickleType, index=True, unique=False)
    # public_view=db.Column(db.Boolean, nullable=False, default=False)

class UserLogging(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=False)
    action = db.Column(db.String(120), index=True, unique=False)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64), index=True)
    lastname = db.Column(db.String(64), index=True)
    username = db.Column(db.String(64), index=True,unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    disk_quota = db.Column(db.Float, nullable=False, default=2.5e+8)
    mailed_files = db.Column( PickleType )
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)
    password_set = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, nullable=False, default=False)
    #confirmed = db.Column(db.Boolean, nullable=False, default=False)
    privacy =  db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    inactive_reason=db.Column(db.String(240))
    password_hash = db.Column(db.String(128))
    multipleapps=db.Column(db.Boolean, nullable=False, default=False)
    notifyme=db.Column(db.Boolean, nullable=False, default=True)
    user_apps = db.Column( PickleType )
    view_apps = db.Column( PickleType )
    domain = db.Column(db.String(120), index=True, unique=False)
    administrator=db.Column(db.Boolean, nullable=False, default=False)


    def __repr__(self):
        return '<Email {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def get_email_validation_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def get_allow_user_token(self, expires_in=600):
        return jwt.encode(
            {'allow_user': self.id, 'uname':self.username, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def verify_email_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def verify_allow_user_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['allow_user']
        except:
            return
        return User.query.get(id)

# @login_manager.user_loader
# def load_user(id):
#     return User.query.get(int(id))

@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""

    if user_id is not None:
        user=User.query.get(user_id)
        if not user.active:
            return None
        r=request.endpoint
        r=r.split("/")[1]
        if ( r in PRIVATE_ROUTES ) and ( r not in PUBLIC_VIEWS ):
            r_obj=PrivateRoutes.query.filter_by(route=r).first()
            if not r_obj :
                return None

            if r_obj.users_domains:
                if user.domain in r_obj.users_domains :
                    return User.query.get(user_id)
            
            if user.id not in r_obj.users :
                return None
                    
        return User.query.get(user_id)
    return None

# @login_manager.unauthorized_handler
# def unauthorized():
#     """Redirect unauthorized users to Login page."""
#     return redirect(f'{app.config["APP_URL"]}/login/')