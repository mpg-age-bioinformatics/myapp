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
from ._utils import META_TAGS, check_email

dashapp = dash.Dash("forgot",url_base_pathname='/forgot/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title="cycshare")# , assets_folder="/flaski/flaski/static/dash/")

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

password_input_2 = dbc.FormGroup(
    [
        dbc.Label("Repeat Password", html_for="input-password-2"),
        dbc.Input(
            type="password",
            id="input-password-2",
            placeholder="Enter password again",
        ),
    ]
)

footer=html.Div([
    dbc.Row( 
        html.Footer( [ html.A("Login", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/login"),
                     html.A("Register", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/register"),
                     html.A("Contact", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/contact")] , 
        style={"margin-top": 5, "margin-bottom": 5, "margin-left": "20px"},
        ),
        style={"justify-content":"center"}
        )
    ])

request_form=[ html.H2("Forgot password", style={'textAlign': 'center'} ),
                username_input,
                html.Div(id="username-feedback"),
                html.Button(id='reset-button', n_clicks=0, children='Reset', style={"width":"auto","margin-top":4, "margin-bottom":4}),
                html.Div(id="reset-feedback") ]

change_form=[ html.H2("Forgot password", style={'textAlign': 'center'} ),
                password_input,
                html.Div(id="pass-power"),
                html.Div(id="pass-feedback"),
                password_input_2,
                html.Div(id="pass2-feedback"),
                html.Button(id='reset-button', n_clicks=0, children='Change password', style={"width":"auto","margin-top":4, "margin-bottom":4}),
                html.Div(id="change-feedback") ]


dashapp.layout=dbc.Row( [
    dbc.Col( md=4),
    dbc.Col( [ dcc.Location(id='url', refresh=False),
               dbc.Card(  dbc.Form(id="forgot-form")
                        , body=True), footer ],
             md=4, align="center", style={ "margin-left":2, "margin-right":2 }),
    dbc.Col( md=4),
],
align="center",
style={"min-height": "100vh", 'verticalAlign': 'center'})


@dashapp.callback(
    Output('forgot-form', 'children'),
    Input('url', 'pathname'))
def verify_email_token(pathname):
    if current_user:
        print(current_user.username)
        import sys ; sys.stdout.flush()
        if current_user.is_authenticated:
            return dcc.Location(pathname="/index/", id='index')

    token=pathname.split("/forgot/")[-1]
    if not token:
        return request_form
    user = User.verify_email_token(token)
    if not user:
        return dbc.Alert( "Could not find account!" ,color="danger")