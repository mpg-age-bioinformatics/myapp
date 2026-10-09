"""Isolated SQLite tests; never load production config or send real email.

Run: python -m unittest discover -s tests -p 'test_email_revalidation.py'
"""
import importlib.util
import ast
from pathlib import Path
import sys
import types
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
import jwt

ROOT = Path(__file__).resolve().parents[1]
package = types.ModuleType('myapp')
package.__path__ = [str(ROOT / 'myapp')]
package.app = Flask('email-lifecycle-test')
package.app.config.update(SQLALCHEMY_DATABASE_URI='sqlite://', SECRET_KEY='test-only-secret-key-not-for-production',
                          APP_URL='https://example.test/v3', APP_TITLE='Test',
                          MAIL_USERNAME_ADDRESS='facility@example.test', TESTING=True)
package.db = SQLAlchemy(package.app)
package.login_manager = LoginManager(package.app)
package.mail = Mail(package.app)
package.PRIVATE_ROUTES = []
package.PUBLIC_VIEWS = []
package.PAGE_PREFIX = '/v3'
sys.modules['myapp'] = package


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


models = load('myapp.models', ROOT / 'myapp/models.py')
lifecycle = load('myapp.email_revalidation', ROOT / 'myapp/email_revalidation.py')
User = models.User


class EmailLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.context = package.app.app_context()
        self.context.push()
        package.db.create_all()
        self.now = datetime.utcnow().replace(microsecond=0)
        self.user = User(username='tester', firstname='Test', email='test@example.test', active=True,
                         registered_on=self.now - timedelta(days=800),
                         confirmed_on=self.now - timedelta(days=800))
        self.user.set_password('original-password')
        package.db.session.add(self.user)
        package.db.session.commit()

    def tearDown(self):
        package.db.session.remove()
        package.db.drop_all()
        self.context.pop()

    def run_job(self, now=None, **kwargs):
        with patch.object(lifecycle.mail, 'send') as send:
            counts = lifecycle.run_email_revalidation(now or self.now, **kwargs)
        return counts, send

    def test_request_and_reminder_and_deactivation(self):
        counts, send = self.run_job()
        self.assertEqual(counts['request'], 1)
        self.assertEqual(send.call_count, 1)
        self.assertEqual(self.user.email_validation_first_sent_on, self.now)
        self.assertEqual(self.run_job()[1].call_count, 0)
        self.assertEqual(self.run_job(self.now + timedelta(days=6))[1].call_count, 0)
        self.assertEqual(self.run_job(self.now + timedelta(days=7))[0]['reminder'], 1)
        self.assertEqual(self.user.email_validation_last_sent_on, self.now + timedelta(days=7))
        self.assertEqual(self.run_job(self.now + timedelta(days=13))[1].call_count, 0)
        self.assertEqual(self.run_job(self.now + timedelta(days=14))[0]['deactivate'], 1)
        self.assertFalse(self.user.check_password('original-password'))
        self.assertEqual(self.user.email_deactivated_on, self.now + timedelta(days=14))
        self.assertEqual(self.run_job(self.now + timedelta(days=15))[1].call_count, 0)

    def test_recent_validation_overrides_old_registration(self):
        self.user.email_validated_on = self.now - timedelta(days=20)
        package.db.session.commit()
        self.assertEqual(self.run_job()[1].call_count, 0)

    def test_new_and_inactive_users_not_mailed(self):
        self.user.registered_on = self.now
        self.user.confirmed_on = self.now
        package.db.session.commit()
        self.assertEqual(self.run_job()[1].call_count, 0)
        self.user.active = False
        self.user.registered_on = self.now - timedelta(days=800)
        self.user.confirmed_on = self.user.registered_on
        package.db.session.commit()
        self.assertEqual(self.run_job()[1].call_count, 0)

    def test_smtp_failure_does_not_start_countdown(self):
        with self.assertLogs(package.app.logger, level='ERROR'), patch.object(lifecycle.mail, 'send', side_effect=RuntimeError('SMTP unavailable')):
            self.assertEqual(lifecycle.run_email_revalidation(self.now)['failed'], 1)
        self.assertIsNone(self.user.email_validation_first_sent_on)
        self.assertEqual(self.run_job()[0]['request'], 1)

    def test_deactivation_email_failure_preserves_password(self):
        self.run_job()
        self.run_job(self.now + timedelta(days=7))
        with self.assertLogs(package.app.logger, level='ERROR'), patch.object(lifecycle.mail, 'send', side_effect=RuntimeError('SMTP unavailable')):
            self.assertEqual(lifecycle.run_email_revalidation(self.now + timedelta(days=14))['failed'], 1)
        self.assertIsNone(self.user.email_deactivated_on)
        self.assertTrue(self.user.check_password('original-password'))

    def test_validation_link_and_replay(self):
        self.run_job()
        token = lifecycle.make_revalidation_token(self.user, self.now, self.now)
        client = package.app.test_client()
        response = client.get('/v3/validate-email/' + token)
        self.assertEqual(response.status_code, 200)
        package.db.session.refresh(self.user)
        self.assertIsNotNone(self.user.email_validated_on)
        self.assertIsNone(self.user.email_validation_first_sent_on)
        self.assertEqual(self.user.email_validation_last_sent_on, self.now)
        self.assertEqual(client.get('/v3/validate-email/' + token).status_code, 400)
        self.assertEqual(self.run_job(self.now + timedelta(days=14))[1].call_count, 0)

    def test_tokens_are_purpose_specific(self):
        registration = self.user.get_email_validation_token()
        reset = self.user.get_reset_password_token()
        self.assertIsNone(User.verify_reset_password_token(registration))
        self.assertIsNone(User.verify_email_token(reset))
        self.assertEqual(User.verify_email_token(registration).id, self.user.id)
        self.run_job()
        annual = lifecycle.make_revalidation_token(self.user, self.now, self.now)
        self.assertIsNone(User.verify_reset_password_token(annual))
        self.assertIsNone(User.verify_email_token(annual))
        self.assertEqual(package.app.test_client().get('/v3/validate-email/' + reset).status_code, 400)

    def test_changed_email_and_expired_tokens_rejected(self):
        self.run_job()
        token = lifecycle.make_revalidation_token(self.user, self.now, self.now)
        self.user.email = 'changed@example.test'
        package.db.session.commit()
        self.assertEqual(package.app.test_client().get('/v3/validate-email/' + token).status_code, 400)
        expired = jwt.encode({'revalidate_email': self.user.id, 'exp': self.now - timedelta(days=1)},
                             package.app.config['SECRET_KEY'], algorithm='HS256')
        self.assertEqual(package.app.test_client().get('/v3/validate-email/' + expired).status_code, 400)

    def test_deactivated_sessions_and_validation_blocked(self):
        self.run_job()
        token = lifecycle.make_revalidation_token(self.user, self.now, self.now)
        self.run_job(self.now + timedelta(days=7))
        self.run_job(self.now + timedelta(days=14))
        with package.app.test_request_context('/'):
            self.assertIsNone(models.load_user(self.user.id))
        self.assertEqual(package.app.test_client().get('/v3/validate-email/' + token).status_code, 400)

    def test_reactivation_requires_password_change(self):
        self.user.email_deactivated_on = self.now
        self.user.password_set = self.now
        self.user.reactivate_after_password_recovery()
        self.assertEqual(self.user.email_deactivated_on, self.now)
        self.user.password_set = self.now + timedelta(seconds=10)
        self.user.set_password('recovered-password')
        self.user.reactivate_after_password_recovery()
        self.assertIsNone(self.user.email_deactivated_on)
        self.assertIsNotNone(self.user.email_validated_on)
        self.assertIsNone(self.user.email_validation_first_sent_on)

    def test_recovery_and_login_callbacks_require_successful_2fa(self):
        from flask import request, session
        from urllib.parse import urlparse

        def callback(filename, name, extra):
            tree = ast.parse((ROOT / 'myapp/routes' / filename).read_text())
            function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
            function.decorator_list = []
            ns = dict(User=User, db=package.db, datetime=datetime, PAGE_PREFIX='/v3',
                      request=request, session=session, url_parse=urlparse,
                      check_email=lambda _: True,
                      dbc=types.SimpleNamespace(Alert=lambda text, **kw: text),
                      dcc=types.SimpleNamespace(Location=lambda **kw: kw))
            ns.update(extra)
            exec(compile(ast.Module(body=[function], type_ignores=[]), filename, 'exec'), ns)
            return ns[name]

        self.user.email_deactivated_on = self.now
        self.user.password_set = self.now
        self.user.otp_enabled = True
        package.db.session.commit()
        reset = callback('forgot.py', 'request_change', {
            'password_check': lambda _: {'passtype': 'strong'}})
        token = self.user.get_reset_password_token()
        reset(1, '/v3/forgot/' + token, 'recovered-password', 'recovered-password')
        self.assertEqual(self.user.email_deactivated_on, self.now)
        logins = []
        extra = {'login_user': lambda *args, **kw: logins.append(args[0].id)}
        login = callback('login.py', 'login_buttom', extra)
        otp = callback('login.py', 'otp_buttoms', extra)
        with package.app.test_request_context('/v3/login/'):
            login(1, self.user.email, 'wrong-password', False, '/v3/login/')
            self.assertEqual(logins, [])
            login(1, self.user.email, 'recovered-password', False, '/v3/login/')
            self.assertEqual(self.user.email_deactivated_on, self.now)
            with patch.object(User, 'verify_totp', return_value=False):
                otp(1, 0, self.user.email, 'recovered-password', False, 'invalid')
            self.assertEqual(self.user.email_deactivated_on, self.now)
            with patch.object(User, 'verify_totp', return_value=True):
                otp(1, 0, self.user.email, 'recovered-password', False, 'valid')
            self.assertIsNone(self.user.email_deactivated_on)
            self.assertEqual(logins, [self.user.id])

    def test_dry_run_has_no_side_effects(self):
        counts, send = self.run_job(dry_run=True)
        self.assertEqual(counts['request'], 1)
        self.assertEqual(send.call_count, 0)
        self.assertIsNone(self.user.email_validation_first_sent_on)

    def test_calendar_year_and_late_reminder(self):
        self.user.registered_on = datetime(2023, 2, 28)
        self.user.confirmed_on = self.user.registered_on
        self.assertIsNone(lifecycle.validation_action(self.user, datetime(2024, 2, 29)))
        self.assertEqual(lifecycle.validation_action(self.user, datetime(2024, 3, 1)), 'request')
        self.user.email_validation_first_sent_on = self.now - timedelta(days=20)
        self.user.email_validation_last_sent_on = self.user.email_validation_first_sent_on
        self.assertEqual(lifecycle.validation_action(self.user, self.now), 'reminder')


if __name__ == '__main__':
    unittest.main()
