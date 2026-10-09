"""Annual email checks. All database timestamps are naive UTC."""
from datetime import datetime, timedelta
import secrets

import jwt
from flask import render_template_string
from flask_mail import Message

from myapp import app, db, mail, PAGE_PREFIX
from myapp.models import User


def validation_action(user, now):
    """Return the next action without sending mail or changing state."""
    if not user.active or user.email_deactivated_on is not None:
        return None
    first = user.email_validation_first_sent_on
    if first is not None:
        if user.email_validated_on and user.email_validated_on >= first:
            return None
        last = user.email_validation_last_sent_on
        if now >= first + timedelta(days=7) and (last is None or last <= first):
            return 'reminder'
        if now >= first + timedelta(days=14):
            return 'deactivate'
        return None
    try:
        cutoff = now.replace(year=now.year - 1)
    except ValueError:  # February 29
        cutoff = now.replace(year=now.year - 1, day=28)
    validated = user.email_validated_on or user.confirmed_on
    if ((user.registered_on and user.registered_on < cutoff)
            or (validated and validated < cutoff)):
        # A recent validation supersedes an old registration date.
        if validated is None or validated < cutoff:
            return 'request'
    return None


def make_revalidation_token(user, first_sent, now):
    deadline = first_sent + timedelta(days=14)
    # If the scheduled job missed the reminder, allow time to use that late link.
    deadline = max(deadline, now + timedelta(days=1))
    return jwt.encode({
        'revalidate_email': user.id,
        'email': user.email,
        'cycle': first_sent.isoformat(timespec='microseconds'),
        'exp': deadline,
    }, app.config['SECRET_KEY'], algorithm='HS256')


def send_lifecycle_email(user, action, first_sent, now):
    """Synchronous: callers record success only after SMTP accepts the message."""
    base = app.config['APP_URL'].rstrip('/')
    title = app.config['APP_TITLE']
    if action == 'deactivate':
        subject = f'[{title}] Your account has been deactivated'
        body = (
            f'Hello {user.firstname or user.username},\n\n'
            'Your account has been deactivated because your email address was not '
            'validated within two weeks of our first request. Your password has '
            'been replaced with a random password.\n\n'
            'You can reactivate your account by using password recovery, setting '
            'a new password, and then logging in (including two-factor '
            'authentication if enabled).\n\n'
            f'Password recovery: {base}/forgot/\n'
        )
    else:
        token = make_revalidation_token(user, first_sent, now)
        deadline = first_sent + timedelta(days=14)
        subject = f'[{title}] ' + ('Reminder: ' if action == 'reminder' else '') + 'Please validate your email address'
        body = (
            f'Hello {user.firstname or user.username},\n\n'
            'Please validate your email address to keep your account accessible. '
            'We request this validation annually.\n\n'
            f'Validate your email: {base}/validate-email/{token}\n\n'
            f'Please validate by {deadline:%Y-%m-%d %H:%M} UTC. '
            'If you do not validate within two weeks of the first request, your '
            'password will be replaced with a random password and your account '
            'will be deactivated. You can subsequently recover access through '
            'password recovery and login.\n'
        )
    message = Message(subject, sender=app.config['MAIL_USERNAME_ADDRESS'],
                      recipients=[user.email], reply_to=app.config['MAIL_USERNAME_ADDRESS'])
    message.body = body
    mail.send(message)


def run_email_revalidation(now=None, dry_run=False):
    now = (now or datetime.utcnow()).replace(microsecond=0)
    counts = dict(request=0, reminder=0, deactivate=0, failed=0)
    ids = [row[0] for row in db.session.query(User.id).filter(
        User.active.is_(True), User.email_deactivated_on.is_(None)).all()]
    db.session.rollback()
    for user_id in ids:
        try:
            # Serialize scheduler runs and validation clicks for each account.
            user = User.query.filter_by(id=user_id).populate_existing().with_for_update().first()
            if user is None:
                db.session.rollback()
                continue
            action = validation_action(user, now)
            if action is None:
                db.session.rollback()
                continue
            if dry_run:
                counts[action] += 1
                db.session.rollback()
                continue
            first = user.email_validation_first_sent_on or now
            send_lifecycle_email(user, action, first, now)
            if action == 'deactivate':
                user.set_password(secrets.token_urlsafe(48))
                user.password_set = now
                user.email_deactivated_on = now
            else:
                user.email_validation_first_sent_on = first
                user.email_validation_last_sent_on = now
            db.session.commit()
            counts[action] += 1
        except Exception:
            db.session.rollback()
            counts['failed'] += 1
            # Never include tokens, passwords or message bodies in logs.
            app.logger.exception('Email lifecycle failed for user id %s', user_id)
    return counts


@app.route(f'{PAGE_PREFIX}/validate-email/<token>', methods=['GET'])
def validate_email_again(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['revalidate_email']
    except (jwt.InvalidTokenError, KeyError, TypeError):
        return validation_response('This validation link is invalid or expired.', 400)
    user = User.query.filter_by(id=user_id).populate_existing().with_for_update().first()
    if (user is None or not user.active or user.email_deactivated_on is not None
            or payload.get('email') != user.email
            or user.email_validation_first_sent_on is None
            or payload.get('cycle') != user.email_validation_first_sent_on.isoformat(timespec='microseconds')):
        db.session.rollback()
        return validation_response('This validation link is no longer valid.', 400)
    user.record_email_validation()
    if user.confirmed_on is None:
        user.confirmed_on = user.email_validated_on
    db.session.commit()
    return validation_response('Your email address has been validated. Thank you!', 200)


def validation_response(message, status):
    return render_template_string(
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Email validation</title><main><h1>Email validation</h1>'
        '<p>{{ message }}</p><a href="{{ login_url }}">Log in</a></main></html>',
        message=message, login_url=f'{PAGE_PREFIX}/login/'), status, {
            'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer'}
