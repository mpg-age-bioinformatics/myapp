from myapp import app, db
from flask_login import current_user
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash_bootstrap_components as dbc
from myapp.models import User
from myapp.email import send_password_reset_email
from datetime import datetime
from ._utils import META_TAGS, check_email, password_check, navbar_A

dashapp = dash.Dash("forgot",url_base_pathname='/forgot/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])# , assets_folder="/flaski/flaski/static/dash/")

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

footer=html.Div(
    [
        dbc.Row( 
            html.Footer( 
                [ 
                    html.A("Login", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/login/"),
                    html.A("Register", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/register/"),
                    html.A("Contact", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/contact/")
                ], 
                style={"margin-top": 5, "margin-bottom": 5, "margin-left": "20px"},
            ),
            style={"justify-content":"center"}
        )
    ]
)

request_form=[ 
    html.H2("Forgot password", style={'textAlign': 'center'} ),
    username_input,
    html.Div(id="username-feedback"),
    html.Button(id='reset-button', n_clicks=0, children='Reset', style={"width":"auto","margin-top":4, "margin-bottom":4}),
    html.Div(id="reset-feedback") 
]

change_form=[ 
    html.H2("Forgot password", style={'textAlign': 'center'} ),
    password_input,
    html.Div(id="pass-power"),
    html.Div(id="pass-feedback"),
    password_input_2,
    html.Div(id="pass2-feedback"),
    html.Button(id='change-button', n_clicks=0, children='Change password', style={"width":"auto","margin-top":4, "margin-bottom":4}),
    html.Div(id="change-feedback") 
]


dashapp.layout=dbc.Row( 
    [
        dbc.Col( 
            [ 
                dcc.Location(id='url', refresh=False),
                dbc.Card(  
                    dbc.Form(id="forgot-form"), 
                    body=True
                    ), 
                footer 
            ],
            md=8, lg=6, xl=4, 
            align="center", 
            style={ "margin-left":2, "margin-right":2 ,'margin-bottom':"50px"}
        ),
        navbar_A
    ],
    align="center",
    justify="center",
    style={"min-height": "95vh", 'verticalAlign': 'center'}
)

@dashapp.callback(
    Output('pass-feedback', 'children'),
    Output('pass2-feedback', 'children'),
    Output('change-feedback', 'children'),
    Input('change-button', 'n_clicks'),
    State('url', 'pathname'),
    State('input-password','value'),
    State('input-password-2','value'),
    prevent_initial_call=True )
def request_change(n_clicks, pathname, passA, passB):
    token=pathname.split("/forgot/")[-1]
    passA_=None
    passB_=None
    submission_=None
    if not token:
        return passA_, passB_, dbc.Alert( "Could not find token!" , style={"textAlign":"center","verticalAlign": "middle"}, color="danger")
    if not passA:
        passA_=dbc.Alert( "*required" ,color="warning")
    else:
        passdic=password_check(passA)
        if passdic["passtype"] != "strong" :
            passA_=dbc.Alert( "please use a strong password" ,color="warning")
    if not passB:
        passB_=dbc.Alert( "*required" ,color="warning")
    elif passA != passB:
        passB_=dbc.Alert( "Passwords do not match" ,color="warning")
    if passA_ or passB_ :
        return passA_, passB_, submission_

    user=User.verify_reset_password_token(token)
    user.password_set=datetime.utcnow()
    user.set_password(passA)
    db.session.commit()
    return passA_, passB_, dcc.Location(pathname="/login/forgot/", id='login')
    

@dashapp.callback(
    Output('pass-power', 'children'),
    Input('input-password', 'value'),
    prevent_initial_call=True)
def check_pass_power(passA):
    passdic=password_check(passA)
    if passdic["passtype"] == "weak":
        return dbc.Alert( "please use a strong password" ,color="danger")
    elif passdic["passtype"] == "medium":
        return dbc.Alert( "please use a strong password" ,color="warning")
    elif passdic["passtype"] == "strong":
        return dbc.Alert( "strong password" ,id="alert-auto", color="success",is_open=True, duration=1500)


@dashapp.callback(
    Output('username-feedback', 'children'),
    Output('reset-feedback', 'children'),
    Input('reset-button', 'n_clicks'),
    State('username', 'value'),
    prevent_initial_call=True )
def request_change(n_clicks, username):
    if not username:
        return dbc.Alert( "*required" ,color="warning"), None
    if check_email(username):
        user=User.query.filter_by(email=username).first()
    else:
        user=User.query.filter_by(username=username).first()
    if not user:
        return dbc.Alert( "Could not find username!" ,color="warning"), None

    send_password_reset_email(user)
    return None, dbc.Alert( "Reset password email sent." ,color="success")


@dashapp.callback(
    Output('forgot-form', 'children'),
    Input('url', 'pathname'))
def verify_email_token(pathname):
    if current_user:
        if current_user.is_authenticated:
            return dcc.Location(pathname="/index/", id='index')

    token=pathname.split("/forgot/")[-1]
    if not token:
        return request_form
    
    user = User.verify_email_token(token)
    if not user:
        return dbc.Alert( "INVALID" , style={"textAlign":"center","verticalAlign": "middle"}, color="danger")
    
    return change_form
