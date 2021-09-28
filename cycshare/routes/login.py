from cycshare import app, db
from flask import session, request
from flask_login import current_user, login_user, logout_user
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from cycshare.models import User
from cycshare.email import send_validate_email
from datetime import datetime
from werkzeug.urls import url_parse
from ._utils import META_TAGS, check_email, navbar_A

dashapp = dash.Dash("login",url_base_pathname='/login/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title="cycshare")# , assets_folder="/flaski/flaski/static/dash/")

username_input = dbc.FormGroup(
    [
        dbc.Label("Username", html_for="username"),
        dbc.Input(type="text", id="username", placeholder="Enter username"),
    ]
)

password_input = dbc.FormGroup(
    [
        dbc.Label("Password", html_for="input-password"),
        dbc.Input(
            type="password",
            id="input-password",
            placeholder="Enter password",
        ),
    ]
)

keppsigned=dcc.Checklist(
    options=[
        {'label': " Keep me signed in.", 'value': 'keep'},
    ],
    value=[],
    id="keepsigned",
    style={"margin-left":"15px"}
)

footer=html.Div([
    dbc.Row( 
        html.Footer( [ html.A("Register", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/register/"),
                     html.A("Forgot Password", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/forgot/"),
                     html.A("Contact", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/contact/")] , 
        style={"margin-top": 5, "margin-bottom": 5, "margin-left": "20px"},
        ),
        style={"justify-content":"center"}
        )
    ])


#[dbc.Form([email_input, password_input])]
dashapp.layout=dbc.Row( [
    dbc.Col( md=2, lg=3, xl=4),
    dbc.Col( [ dcc.Location(id='url', refresh=False),
               dbc.Card(  dbc.Form([ html.H2("Login", style={'textAlign': 'center'} ),
                                    html.Div(id="token-feedback"),
                                    username_input,
                                    html.Div(id="username-feedback"),
                                    password_input,
                                    html.Div(id="pass-feedback"),
                                    dbc.Row( keppsigned ),
                                    html.Button(id='submit-button-state', n_clicks=0, children='Login', style={"width":"auto","margin-top":4, "margin-bottom":4}),
                                    html.Div(id="submission-feedback"),
                                ])
                        , body=True), footer ],
             md=8, lg=6, xl=4, align="center", style={ "margin-left":2, "margin-right":2 }),
    dbc.Col( md=2, lg=3, xl=4), navbar_A
],
align="center",
style={"min-height": "100vh", 'verticalAlign': 'center'})

@dashapp.callback(
    Output('token-feedback', 'children'),
    Input('url', 'pathname'))
def verify_email_token(pathname):
    if pathname == "/login/forgot/":
        return dbc.Alert( "You're password has been reset." ,color="success")
    if pathname == "/login/logout/":
        return dbc.Alert( "You've been logged out." ,color="primary")
    if "/login/admin/" in pathname:
        token=pathname.split("/login/admin/")[-1]
        if token:
            user=User.verify_allow_user_token(token)
            if user:
                user.active=True
                db.session.add(user)
                db.session.commit()
                send_validate_email(user, step="user")
                return dbc.Alert( user.email ,color="primary")
            else:
                return dbc.Alert( "Could not find user!" ,color="danger")
        else:
            return dbc.Alert( "Could not find user!" ,color="danger")

    if current_user:
        if current_user.is_authenticated:
            return dcc.Location(pathname="/index/", id='index')

    token=pathname.split("/login/")[-1]
    if not token:
        return None
    user = User.verify_email_token(token)
    if not user:
        return dbc.Alert( "Could not find account!" ,color="danger")
    if user.confirmed_on:
        if not user.active:
            msg="This account has already been confirmed. cycshare is currently for beta testers only. Our site administrator will soon review your contact information and enable your account. Thanks!"
        else:
            msg="This account has already been confirmed. Please login."
        return dbc.Alert( msg ,color="warning")
    user.confirmed_on = datetime.now()
    db.session.add(user)
    db.session.commit()
    return dbc.Alert( 'You have confirmed your account. Thanks!' ,color="success")

# @dashapp.callback(
#     Output('logged-feedback', 'children'),
#     Input('url', 'pathname'))
# def check_logged(pathname):
#     if current_user:
#         if current_user.is_authenticated:
#             return dcc.Location(pathname="/index/", id='index')

@dashapp.callback(
    Output('username-feedback', 'children'),
    Output('pass-feedback', 'children'),
    Output('submission-feedback', 'children'),
    Input('submit-button-state', 'n_clicks'),
    State('username', 'value'),
    State('input-password', 'value'),
    State('keepsigned', 'value'),
    prevent_initial_call=True
    )
def login_buttom(n_clicks, username, passA, keepsigned):
    username_=None
    passA_=None
    submission_=None

    if not username:
        username_=dbc.Alert( "*required" ,color="warning")
    if not passA:
        passA_=dbc.Alert( "*required" ,color="warning")
    if username_ or passA_:
        return username_, passA_, submission_

    if check_email(username):
        user=User.query.filter_by(email=username).first()
    else:
        user=User.query.filter_by(username=username).first()
    if not user:
        return dbc.Alert( "Could not find username!" ,color="warning"), passA_, submission_

    if not user.check_password(passA):
        return  username_, dbc.Alert( "Wrong password!" ,color="warning"), submission_

    if not user.confirmed_on : 
        return username_, passA_, dbc.Alert( "Please confirm your email address." ,color="warning")
    
    if not user.active:
        return username_, passA_, dbc.Alert( "This account is not active." ,color="warning")

    if keepsigned :
        keepsigned_=True
    else:
        keepsigned_=False

    login_user(user, remember=keepsigned_)
    session.permanent = keepsigned_

    next_page = request.args.get('next')
    db.session.add(user)
    db.session.commit()
    if not next_page or url_parse(next_page).netloc != '':
        next_page = '/index/'
    return None, None, dcc.Location(pathname=next_page, id='index')



