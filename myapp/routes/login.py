from myapp import app, db
from flask import session, request
from flask_login import current_user, login_user, logout_user
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash_bootstrap_components as dbc
from myapp.models import User
from myapp.email import send_validate_email
from datetime import datetime
from werkzeug.urls import url_parse
from ._utils import META_TAGS, check_email, navbar_A

dashapp = dash.Dash("login",url_base_pathname='/login/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])# , assets_folder="/flaski/flaski/static/dash/")

username_input = html.Div(
    [
        dbc.Label("Username", html_for="username"),
        dbc.Input(type="text", id="username", placeholder="Enter username"),
    ],
    style={"margin-bottom":"8px"}
)

password_input = html.Div(
    [
        dbc.Label("Password", html_for="input-password"),
        dbc.Input(
            type="password",
            id="input-password",
            placeholder="Enter password",
        ),
    ],
    style={"margin-bottom":"8px"}
)

keppsigned=dcc.Checklist(
    options=[
        {'label': " Keep me signed in.", 'value': 'keep'},
    ],
    value=[],
    id="keepsigned",
    # style={"margin-left":"0px"}
    style={"margin-bottom":"8px"}

)

footer=html.Footer(
    dbc.Row(
        [
            dbc.Col(
                [
                    html.A("Register", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/register/"),
                    html.A("Forgot Password", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/forgot/"),
                    html.A("Contact", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/contact/")
                ],
                style={ 'display':'flex', 'justifyContent':'center'}
            )
        ],
        justify="center",
        align="center"
    )
)


dashapp.layout=html.Div(
    [
        dcc.Location(id='url', refresh=False),
        html.Div(id="page-content", style={'display': 'block'}),
        html.Div(id="otp-content", style={'display': 'none'}) 
    ]
)

@dashapp.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'))
def generate_content(pathname):
    if current_user:
        if current_user.is_authenticated:
            return dcc.Location(pathname="/home/", id='index')
    return dbc.Row( 
        [
            dbc.Col( 
                [ 
                    dbc.Card(
                        dbc.Form(
                            [ 
                                html.H2("Login", style={'textAlign': 'center'} ),
                                html.Div(id="token-feedback"),
                                username_input,
                                html.Div(id="username-feedback"),
                                password_input,
                                html.Div(id="pass-feedback"),
                                dbc.Row( keppsigned ),
                                html.Button(id='submit-button-state', n_clicks=0, children='Login', style={"width":"auto","margin-top":4, "margin-bottom":4}),
                                html.Div(id="submission-feedback", style={"margin-top":"10px"}),
                            ]
                        )
                        , body=True
                    ),
                    footer 
                ],
                sm=9,md=6, lg=5, xl=5, 
                align="center",
                style={ "margin-left":2, "margin-right":2 ,'margin-bottom':"50px"}
            ),
            navbar_A
        ],
        align="center",
        justify="center",
        style={"min-height": "95vh", 'verticalAlign': 'center'}
    ) #, 


@dashapp.callback(
    Output('otp-content', 'children'),
    Input('url', 'pathname'))
def generate_otp_content(pathname):
    # otp = dbc.FormFloating(
    #     [
    #         dbc.Input(type="text", id="otp", placeholder="2FA token", style={"max-width":"150px","margin":"2px", "height":"40px"}),
    #     ]
    # )

    otp_content=dbc.Row( 
        [
            dbc.Col( 
                [ 
                    dbc.Card(  
                        [ 
                            dbc.Row(
                                dbc.Col(
                                    dbc.Input(type="text", id="otp", placeholder="2FA token", style={"width":"100%","margin-left":"4px", "padding-right":"20px","height":"40px"}), #
                                ),
                                justify="center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Button(id='submit-otp-button', n_clicks=0, children='Submit', color="secondary", className="me-1", style={"width":"100%","margin":"4px","height":"40px"}),
                                        width=6
                                    ),
                                    dbc.Col(
                                        dbc.Button(id='cancel-otp-button', n_clicks=0, children='Cancel', color="secondary", className="me-1",  style={"width":"100%","margin":"4px","height":"40px"}),
                                        width=6,
                                    )
                                ],
                                # style={ 'display':'flex', 'justifyContent':'center'}
                                className="g-1",
                                justify="center",
                            ),
                            dbc.Row(
                                html.Div(id="otp-feedback", style={"margin":"10px","width":"100%"}),
                                justify="center",
                            )
                        ],
                        # justify="center",
                        # className="g-2", style={"height":"10px" }
                        # ),
                        # ],
                        body=True, 
                        className="border-0",
                        style={ "max-width":"300px"}
                    ) 
                ], 
                xs=12 ,sm=8,md=6, lg=5, xl=4, 
                align="center", 
                style={ "margin-left":2, "margin-right":2 ,'margin-bottom':"50px", 'display':'flex', 'justifyContent':'center'}
            ),
            navbar_A
        ],
        align="center",
        justify="center",
        style={"min-height": "95vh", 'verticalAlign': 'center'}
    )
    return otp_content


@dashapp.callback(
    Output('token-feedback', 'children'),
    Input('url', 'pathname'))
def verify_email_token(pathname):
    if pathname == "/login/email/":
        return dbc.Alert( "Please confirm your email address." ,color="primary")
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
            return dcc.Location(pathname="/home/", id='index')

    token=pathname.split("/login/")[-1]
    if not token:
        return None
    user = User.verify_email_token(token)
    if not user:
        return dbc.Alert( "Could not find account!" ,color="danger")
    if user.confirmed_on:
        if not user.active:
            msg=f'This account has already been confirmed but is currently not active.'
        else:
            msg="This account has already been confirmed. Please login."
        return dbc.Alert( msg ,color="warning" )
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
    Output('page-content', 'style'),
    Output('otp-content', 'style'),
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
    page_={'display': 'block'}
    otp_={'display': 'none'}        

    if n_clicks==0:
        return username_, passA_, submission_, page_, otp_

    if not username:
        username_=dbc.Alert( "*required" ,color="warning")
    if not passA:
        passA_=dbc.Alert( "*required" ,color="warning")
    if username_ or passA_:
        return username_, passA_, submission_, page_, otp_

    if check_email(username):
        user=User.query.filter_by(email=username).first()
    else:
        user=User.query.filter_by(username=username).first()
    if not user:
        return dbc.Alert( "Could not find username!" ,color="warning"), submission_, passA_,  page_, otp_

    if not user.check_password(passA):
        return  username_, dbc.Alert( "Wrong password!" ,color="warning"), submission_, page_, otp_

    if not user.confirmed_on : 
        return username_, passA_, dbc.Alert( "Please confirm your email address." ,color="warning"), page_, otp_
    
    if not user.active:
        return username_, passA_, dbc.Alert( "This account is not active." ,color="warning"), page_, otp_

    if keepsigned :
        keepsigned_=True
    else:
        keepsigned_=False

    if user.otp_enabled:
        return username_, passA_, submission_ , otp_ , page_      

    login_user(user, remember=keepsigned_)
    session.permanent = keepsigned_

    next_page = request.args.get('next')
    db.session.add(user)
    db.session.commit()
    if not next_page or url_parse(next_page).netloc != '':
        next_page = '/home/'
    return None, None, dcc.Location(pathname=next_page, id='index'), page_, otp_



@dashapp.callback(
    Output('otp-feedback', 'children'),
    Input('submit-otp-button', 'n_clicks'),
    Input('cancel-otp-button', 'n_clicks'),
    State('username', 'value'),
    State('input-password', 'value'),
    State('keepsigned', 'value'),
    State('otp', 'value'),
    prevent_initial_call=True
    )
def otp_buttoms(otp_clicks, cancel_clicks, username, passA, keepsigned, otp):
    if cancel_clicks:
        dcc.Location(pathname="/index/", id='index', refresh=True)
    if otp_clicks:
        went_wrong=dbc.Alert( "Something went wrong!" ,color="danger", style={"width":"100%"})
        not_verified=dbc.Alert( "Could not verify token." ,color="danger", style={"width":"100%"})

        if (not username ) or ( not passA ) or ( not otp ) :
            return went_wrong

        if check_email(username):
            user=User.query.filter_by(email=username).first()
        else:
            user=User.query.filter_by(username=username).first()
        if not user:
            return went_wrong

        if not user.check_password(passA):
            return  went_wrong

        if not user.confirmed_on : 
            return went_wrong
        
        if not user.active:
            return went_wrong

        if keepsigned :
            keepsigned_=True
        else:
            keepsigned_=False

        if user.otp_enabled:
            if not user.verify_totp(otp) :
                if user.otp_backup :
                    if not user.check_backup_tokens(otp) :
                        return not_verified
                else:
                    return not_verified

        login_user(user, remember=keepsigned_)
        session.permanent = keepsigned_

        next_page = request.args.get('next')
        db.session.add(user)
        db.session.commit()
        if not next_page or url_parse(next_page).netloc != '':
            next_page = '/home/'
        return dcc.Location(pathname=next_page, id='index')

    elif cancel_clicks :
        return dcc.Location(pathname="/index/", id='index', refresh=True)
    
    return None

