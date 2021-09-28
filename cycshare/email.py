from threading import Thread
from flask import render_template
from cycshare import app
from flask_mail import Message
from cycshare import mail
from werkzeug.utils import secure_filename
import io

APP_NAME=app.config['APP_NAME']
APP_URL=app.config['APP_URL']

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body, reply_to, attachment=None, attachment_path=None, attachment_type=None, open_type="rb"):
    msg = Message(subject, sender=sender, recipients=recipients, reply_to = reply_to)
    msg.body = text_body
    msg.html = html_body
    if attachment:
        if type(attachment) == str:
            filename=attachment
        else:
            filename=attachment.filename
        with open(attachment_path, open_type) as f: 
            msg.attach(
                secure_filename(filename),
                attachment_type,
                f.read() )
        
    Thread(target=send_async_email, args=(app, msg)).start()

def send_contact(firstname, lastname, email, msg):
    send_email(f'[{APP_NAME}] contact',
                sender=app.config['MAIL_USERNAME'],
               recipients=app.config['ADMINS'],
               text_body=render_template('email/contact.txt',
                                         firstname=firstname, lastname=lastname, email=email, msg=msg),
               html_body=render_template('email/contact.html',
                                         firstname=firstname, lastname=lastname, email=email, msg=msg),\
               reply_to=app.config['MAIL_USERNAME'] )
    send_email(f'[{APP_NAME}] contact',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email],
            text_body=render_template('email/contact_user.txt',
                                        firstname=firstname, msg=msg, app_name=APP_NAME, app_url=APP_URL),
            html_body=render_template('email/contact_user.html',
                                        firstname=firstname, msg=msg, app_name=APP_NAME, app_url=APP_URL),\
            reply_to=app.config['MAIL_USERNAME'] )

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(f'[{APP_NAME}] Reset Your Password',
               sender=app.config['MAIL_USERNAME'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token, app_name=APP_NAME, app_url=APP_URL),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token, app_name=APP_NAME, app_url=APP_URL),\
               reply_to=app.config['MAIL_USERNAME'] )

def send_validate_email(user, step="user"):
    token = user.get_email_validation_token()
    token_= user.get_allow_user_token()
    if step=="user":
        send_email(f'Welcome to {APP_NAME}!',
                sender=app.config['MAIL_USERNAME'],
                recipients=[user.email],
                text_body=render_template('email/validate_email.txt',
                                            user=user, token=token, app_name=APP_NAME, app_url=APP_URL),
                html_body=render_template('email/validate_email.html',
                                            user=user, token=token, app_name=APP_NAME, app_url=APP_URL),\
                reply_to=app.config['MAIL_USERNAME'] )
    elif step=="admin":
        send_email(f'[{APP_NAME}] New user registration',
                sender=app.config['MAIL_USERNAME'],
                recipients=app.config['ADMINS'],
                text_body=render_template('email/new_user.txt',
                                            user=user, token=token_, app_name=APP_NAME, app_url=APP_URL),
                html_body=render_template('email/new_user.html',
                                            user=user, token=token_, app_name=APP_NAME, app_url=APP_URL),\
                reply_to=app.config['MAIL_USERNAME'] )                    