from myapp import app, db, PAGE_PREFIX
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash_bootstrap_components as dbc
from myapp.models import User
from myapp.email import send_validate_email
from datetime import datetime
from ._utils import META_TAGS, check_email, password_check, navbar_A
from flask_login import current_user
from sqlalchemy.exc import IntegrityError


dashapp = dash.Dash("register", url_base_pathname=f'{PAGE_PREFIX}/register/',meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title="Register", assets_folder=app.config["APP_ASSETS"])# , assets_folder="/flaski/flaski/static/dash/")

firstname_input = html.Div(
    [
        dbc.Label("First name", html_for="first_name"),
        dbc.Input(type="text", id="first_name", placeholder="First name"),
    ],
    style={"margin-bottom":"8px"}
)

lastname_input = html.Div(
    [
        dbc.Label("Last name", html_for="last_name"),
        dbc.Input(type="text", id="last_name", placeholder="Last name"),
    ],
    style={"margin-bottom":"8px"}
)

username_input = html.Div(
    [
        dbc.Label("Username", html_for="username"),
        dbc.Input(type="text", id="username", placeholder="username"),
    ],
    style={"margin-bottom":"8px"}
)

email_input = html.Div(
    [
        dbc.Label("Email", html_for="input-email"),
        dbc.Input(type="email", id="input-email", placeholder="Enter email"),
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

password_input_2 = html.Div(
    [
        dbc.Label("Repeat Password", html_for="input-password-2"),
        dbc.Input(
            type="password",
            id="input-password-2",
            placeholder="Enter password again",
        ),
    ],
    style={"margin-bottom":"8px"}
)

read=dcc.Checklist(
    options=[
        {'label': " I've read the", 'value': 'useragrees'},
    ],
    value=[],
    id="agreement",
    style={"margin-bottom":"8px"}
)


footer=html.Footer(
    dbc.Row(
        [
            dbc.Col(
               [ 
                    html.A("Login", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href=f"{PAGE_PREFIX}/login/"),
                    html.A("Forgot Password", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href=f"{PAGE_PREFIX}/forgot/"),
                    html.A("Contact", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href=f"{PAGE_PREFIX}/contact/")
                ] , 
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
        html.Div(id="page-content")
    ]
)

@dashapp.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'))
def generate_content(pathname):
    if current_user:
        if current_user.is_authenticated:
            return dcc.Location(pathname=f"{PAGE_PREFIX}/home/", id='index')
    return dbc.Row( 
        [
            dbc.Col( 
                [ 
                    html.Div(id="app_access"),
                    html.Div(id="logged-feedback"),
                    dbc.Card(  
                        dbc.Form(
                            [
                                html.H2("Register", style={'textAlign': 'center'} ),
                                dbc.Row(
                                    [ 
                                        dbc.Col(
                                            [ 
                                                firstname_input,
                                                html.Div(id="firstname-feedback")
                                            ]
                                        ),  
                                        dbc.Col(
                                            [
                                                lastname_input,
                                                html.Div(id="lastname-feedback")
                                            ] 
                                        )
                                    ] 
                                ),
                                username_input,
                                html.Div(id="username-feedback"),
                                email_input,
                                html.Div(id="email-feedback"),
                                password_input,
                                html.Div(id="pass-power"),
                                html.Div(id="pass-feedback"),
                                password_input_2,
                                html.Div(id="pass2-feedback"),
                                dbc.Row(
                                    dbc.Col(
                                        [ 
                                            read , 
                                            html.A("Privacy Statment.", href=f"{PAGE_PREFIX}/privacy/",style={"margin-left":"4px",'whiteSpace': 'pre-wrap'})
                                        ],
                                        style={ 'display':'flex', 'justifyContent':'left'}
                                    )
                                ),
                                html.Div(id="checkbox-feedback"),
                                html.Button(id='submit-button-state', n_clicks=0, children='Submit', style={"width":"auto","margin-top":4, "margin-bottom":4}),
                                html.Div(id="submission-feedback"),
                            ]
                        )
                        , body=True
                    ), 
                    footer 
                ],
                sm=9,md=7, lg=5, xl=5, 
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
    Output('logged-feedback', 'children'),
    Input('url', 'pathname'))
def check_logged(pathname):
    if current_user:
        if current_user.is_authenticated:
            return dcc.Location(pathname=f"{PAGE_PREFIX}/home/", id='index')

@dashapp.callback(
    Output('pass-power', 'children'),
    Input('input-password', 'value'),
    prevent_initial_call=True)
def check_pass_power(passA):
    passdic=password_check(passA)
    if passdic["passtype"] == "short":
        return dbc.Alert( "password is too short" ,color="danger")
    elif passdic["passtype"] == "digit_none":
        return dbc.Alert( "password must contain at least one digit" ,color="warning")
    elif passdic["passtype"] == "case_none":
        return dbc.Alert( "password must contain at least one lowercase and uppercase letter" ,color="warning")
    elif passdic["passtype"] == "symbol_none":
        return dbc.Alert( "password must contain at least one symbol" ,color="warning")
    elif passdic["passtype"] == "strong":
        return dbc.Alert( "strong password" ,id="alert-auto", color="success",is_open=True, duration=1500)

@dashapp.callback(
    Output('username', 'value'),
    Input('first_name', 'value'),
    Input('last_name', 'value'),
    prevent_initial_call=True)
def make_username(first_name,last_name):
    uname=None
    if first_name:
        uname=str(first_name)
    if last_name:
        if first_name:
            uname=str(first_name)+" "+str(last_name)
    return uname

@dashapp.callback(
    Output("alert-auto", "is_open"),
    [Input("alert-toggle-auto", "n_clicks")],
    [State("alert-auto", "is_open")],
)
def toggle_alert(n, is_open):
    if n:
        return not is_open
    return is_open

@dashapp.callback(
    Output('firstname-feedback', 'children'),
    Output('lastname-feedback', 'children'),
    Output('username-feedback', 'children'),
    Output('email-feedback', 'children'),
    Output('pass-feedback', 'children'),
    Output('pass2-feedback', 'children'),
    Output('checkbox-feedback', 'children'),
    Output('submission-feedback', 'children'),
    Input('submit-button-state', 'n_clicks'),
    State('first_name', 'value'),
    State('last_name', 'value'),
    State('username', 'value'),
    State('input-email', 'value'),
    State('input-password', 'value'),
    State('input-password-2', 'value'),
    State('agreement', 'value'),
    prevent_initial_call=True
    )
def submit_register(n_clicks,first_name, last_name, username, email,passA, passB, agree):
    first_name_=None
    last_name_=None
    username_=None
    email_=None
    passA_=None
    passB_=None
    agree_=None
    submission_=None

    if not first_name:
        first_name_=dbc.Alert( "*required" ,color="warning") # style={"font-size":"10px"}
    if not last_name:
        last_name_=dbc.Alert( "*required" ,color="warning")
    if not username:
        username_=dbc.Alert( "*required" ,color="warning")
    else:
        usernameq=User.query.filter_by(username=username).first()
        if usernameq:
            if usernameq.username == username :
                username_=dbc.Alert( "Username already in use." ,color="warning")
    if not email:
        email_=dbc.Alert( "*required" ,color="warning")
    elif not check_email(email):
        email_=dbc.Alert( "invalid email address" ,color="warning")
    else:
        useremail = User.query.filter_by(email=email).first()
        useremail=str(useremail).split(' ')[-1].split(">")[0]
        if email == useremail:
            email_=dbc.Alert( "email already in use" ,color="warning")
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

    if not agree:
        agree_=dbc.Alert( "*required" ,color="warning")
    if first_name_ or last_name_ or username_ or email_ or passA_ or passB_ or agree_ or submission_ :
        return first_name_,last_name_,username_,email_,passA_,passB_,agree_,submission_

    user = User(firstname=first_name,\
        lastname=last_name,\
        username=username,\
        email=email,\
        domain=email.split("@")[-1],\
        privacy=True)
    user.set_password(passA)
    user.registered_on=datetime.utcnow()
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if "ix_user_username" in str(e.orig):
            username_ = dbc.Alert("Username already in use.", color="warning")
        elif "email" in str(e.orig):
            email_ = dbc.Alert("Email already in use.", color="warning")
        else:
            submission_ = dbc.Alert("A database error occurred.", color="danger")
        return first_name_, last_name_, username_, email_, passA_, passB_, agree_, submission_

    if app.config['PREAUTH'] : 
        send_validate_email(user, step="admin")
    else:
        user.active=True
        db.session.add(user)
        db.session.commit()
        send_validate_email(user, step="user")

    # submission_=dbc.Alert( "Success! To finish your registration please check your email." , style={"margin-top":"20px"},color="success")
    return first_name_,last_name_,username_, email_,passA_,passB_,agree_, dcc.Location(pathname=f"{PAGE_PREFIX}/login/success/", id='index')


