from threading import Thread
from flask import render_template
from myapp import app, mail
from flask_mail import Message
from werkzeug.utils import secure_filename
from datetime import datetime
import io
import os
import requests

APP_NAME=app.config['APP_NAME']
APP_URL=app.config['APP_URL']
APP_TITLE=app.config['APP_TITLE']

SLACK_HOOK=app.config['SLACK_HOOK']
EMAIL_LOG_DIR=os.path.join(app.config["USERS_DATA"], 'email_logs')
SEND_FAILED_FILE=os.path.join(EMAIL_LOG_DIR, 'failed.log')
SEND_SUCCESS_FILE=os.path.join(EMAIL_LOG_DIR, 'success.log')

def write_email_log(file_path, msg, e=None):
    try:
        os.makedirs(EMAIL_LOG_DIR, exist_ok=True)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_path, "a") as file:
            file.write(f"Time:" + str(current_time) + "\n")
            file.write("Subject: " + str(msg.subject) + "\n")
            file.write("Sender: " + str(msg.sender) + "\n")
            file.write("Recipients: " + str(msg.recipients) + "\n")
            file.write("Reply-To: " + str(msg.reply_to) + "\n")
            file.write("Body: " + str(msg.body) + "\n")
            if e is not None:
                file.write(f"Exception: {str(e)} \n")
            file.write("-" * 50 + "\n")

        # keep the log file size in check, max 500kb
        if os.path.exists(file_path) and os.path.getsize(file_path) > 512000:
            with open(file_path, "r+") as file:
                lines = file.readlines()
                if len(lines) > 500:
                    file.seek(0)
                    file.writelines(lines[500:])
                    file.truncate()
    except Exception as e:
        print(f"Failed to write email log to file: {e}")

def send_slack_notification(slack_hook, msg, e=None):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = (
            f"*Flaski Email Sending Failed!*\n\n"
            f"*Time:* {current_time}\n"
            f"*Subject:* {str(msg.subject)}\n"
            f"*Sender:* {str(msg.sender)}\n"
            f"*Recipients:* {str(msg.recipients)}\n"
            f"*Reply-To:* {str(msg.reply_to)}\n"
            f"*Body:* {str(msg.body)}\n"
        )
        if e is not None:
            message += f"*Exception:* {str(e)}\n"
        
        payload = {
            "text": message
        }
        headers = {"Content-Type": "application/json"}
        requests.post(slack_hook, json=payload, headers=headers)
    except:
        pass

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            write_email_log(SEND_SUCCESS_FILE, msg)
        except Exception as e: 
            write_email_log(SEND_FAILED_FILE, msg, e)
            if SLACK_HOOK is not None:
                send_slack_notification(SLACK_HOOK, msg, e)

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
    send_email(f'[{APP_TITLE}] contact',
                sender=app.config['MAIL_USERNAME_ADDRESS'],
               recipients=app.config['ADMINS'],
               text_body=render_template('email/contact.txt',
                                         firstname=firstname, lastname=lastname, email=email, msg=msg),
               html_body=render_template('email/contact.html',
                                         firstname=firstname, lastname=lastname, email=email, msg=msg),\
               reply_to=app.config['MAIL_USERNAME_ADDRESS'] )
    send_email(f'[{APP_TITLE}] contact',
            sender=app.config['MAIL_USERNAME_ADDRESS'],
            recipients=[email],
            text_body=render_template('email/contact_user.txt',
                                        firstname=firstname, msg=msg, app_name=APP_TITLE, app_url=APP_URL),
            html_body=render_template('email/contact_user.html',
                                        firstname=firstname, msg=msg, app_name=APP_TITLE, app_url=APP_URL),\
            reply_to=app.config['MAIL_USERNAME_ADDRESS'] )

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(f'[{APP_TITLE}] Reset Your Password',
               sender=app.config['MAIL_USERNAME_ADDRESS'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token, app_name=APP_TITLE, app_url=APP_URL),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token, app_name=APP_TITLE, app_url=APP_URL),\
               reply_to=app.config['MAIL_USERNAME_ADDRESS'] )

def send_validate_email(user, step="user"):
    token = user.get_email_validation_token()
    token_= user.get_allow_user_token()
    if step=="user":
        send_email(f'Welcome to {APP_TITLE}!',
                sender=app.config['MAIL_USERNAME_ADDRESS'],
                recipients=[user.email, app.config['MAIL_USERNAME_ADDRESS']],
                text_body=render_template('email/validate_email.txt',
                                            user=user, token=token, app_name=APP_TITLE, app_url=APP_URL),
                html_body=render_template('email/validate_email.html',
                                            user=user, token=token, app_name=APP_TITLE, app_url=APP_URL),\
                reply_to=app.config['MAIL_USERNAME_ADDRESS'] )
    elif step=="admin":
        send_email(f'[{APP_TITLE}] New user registration',
                sender=app.config['MAIL_USERNAME_ADDRESS'],
                recipients=app.config['ADMINS'],
                text_body=render_template('email/new_user.txt',
                                            user=user, token=token_, app_name=APP_TITLE, app_url=APP_URL),
                html_body=render_template('email/new_user.html',
                                            user=user, token=token_, app_name=APP_TITLE, app_url=APP_URL),\
                reply_to=app.config['MAIL_USERNAME_ADDRESS'] )   

def send_validate_change_email(user):
    token = user.get_email_validation_token()
    send_email(f'Welcome to {APP_TITLE}!',
            sender=app.config['MAIL_USERNAME_ADDRESS'],
            recipients=[user.email],
            text_body=render_template('email/validate_change_email.txt',
                                        user=user, token=token, app_name=APP_TITLE, app_url=APP_URL),
            html_body=render_template('email/validate_change_email.html',
                                        user=user, token=token, app_name=APP_TITLE, app_url=APP_URL),\
            reply_to=app.config['MAIL_USERNAME_ADDRESS'] )
            
    send_email(f'[{APP_TITLE}] contact',
                sender=app.config['MAIL_USERNAME_ADDRESS'],
               recipients=app.config['ADMINS'],
               text_body=render_template('email/general.txt',
                                         firstname=current_user.firstname, body=body,app_name=APP_TITLE),
               html_body=render_template('email/general.html',
                                         firstname=current_user.firstname, body=body,app_name=APP_TITLE),\
               reply_to=app.config['MAIL_USERNAME_ADDRESS'] )