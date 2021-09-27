from cycshare import app, db
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from cycshare.models import User, UserLogging
from cycshare.email import send_password_reset_email, send_validate_email, send_help_email
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import json
from flask import session
from ._utils import META_TAGS
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def check_email(email):
    # pass the regular expression
    # and the string into the fullmatch() method
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

    # overall result
    password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error or symbol_error )

    if length_error or digit_error :
        pass_type="weak"
    elif uppercase_error or lowercase_error or symbol_error:
        pass_type="medium"
    else:
        pass_type="strong"   

    return {
        'password_ok' : password_ok,
        'length_error' : length_error,
        'digit_error' : digit_error,
        'uppercase_error' : uppercase_error,
        'lowercase_error' : lowercase_error,
        'symbol_error' : symbol_error,
        'passtype' : pass_type
    }


dashapp = dash.Dash("register",url_base_pathname='/register/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title="cycshare")# , assets_folder="/flaski/flaski/static/dash/")

firstname_input = dbc.FormGroup(
    [
        dbc.Label("First name", html_for="first_name"),
        dbc.Input(type="text", id="first_name", placeholder="First name"),
    ]
)

lastname_input = dbc.FormGroup(
    [
        dbc.Label("Last name", html_for="last_name"),
        dbc.Input(type="text", id="last_name", placeholder="Last name"),
    ]
)

username_input = dbc.FormGroup(
    [
        dbc.Label("Username", html_for="username"),
        dbc.Input(type="text", id="username", placeholder="username"),
    ]
)



email_input = dbc.FormGroup(
    [
        dbc.Label("Email", html_for="input-email"),
        dbc.Input(type="email", id="input-email", placeholder="Enter email"),
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

read=dcc.Checklist(
    options=[
        {'label': " I've read the", 'value': 'useragrees'},
    ],
    value=[],
    id="agreement",
    style={"margin-left":"15px"}
)

footer=html.Div([
    dbc.Row( 
        html.Footer( [ html.A("Login", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/login"),
                     html.A("Forgot Password", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/forgotpassword"),
                     html.A("Contact", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/contact")] , 
        style={"margin-top": 5, "margin-bottom": 5, "margin-left": "20px"},
        ),
        style={"justify-content":"center"}
        )
    ])


#[dbc.Form([email_input, password_input])]
dashapp.layout=dbc.Row( [
    dbc.Col( md=4),
    dbc.Col( [ html.Div(id="app_access"),
               dbc.Card(  dbc.Form([ html.H2("Register", style={'textAlign': 'center'} ),
                                    dbc.Row([ 
                                        dbc.Col([ firstname_input,html.Div(id="firstname-feedback")] ),  
                                        dbc.Col([ lastname_input,html.Div(id="lastname-feedback")] )] ),
                                    username_input,
                                    html.Div(id="username-feedback"),
                                    email_input,
                                    html.Div(id="email-feedback"),
                                    password_input,
                                    html.Div(id="pass-power"),
                                    html.Div(id="pass-feedback"),
                                    password_input_2,
                                    html.Div(id="pass2-feedback"),
                                    dbc.Row([ read , 
                                              html.A("User Agreement and Data Privacy Statment.", href="https://www.sapo.pt",style={"margin-left":"4px",'whiteSpace': 'pre-wrap'})]),
                                    html.Div(id="checkbox-feedback"),
                                    html.Button(id='submit-button-state', n_clicks=0, children='Submit', style={"width":"auto","margin-top":4, "margin-bottom":4}),
                                    html.Div(id="submission-feedback"),
                                ])
                        , body=True), footer ],
             md=4, align="center"),
    dbc.Col( md=4),
],
align="center",
style={"min-height": "100vh", 'verticalAlign': 'center'})

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
    if not passB:
        passB_=dbc.Alert( "*required" ,color="warning")
    elif passA_ != passB_:
        passB_=dbc.Alert( "Passwords do not match" ,color="warning")
    if not agree:
        agree_=dbc.Alert( "*required" ,color="warning")
    if first_name_ or last_name_ or username_ or email_ or passA_ or passB_ or agree_ or submission_ :
        return first_name_,last_name_,username_,email_,passA_,passB_,agree_,submission_

    user = User(firstname=first_name,\
        lastname=last_name,\
        username=username,\
        email=email,\
        privacy=True)
    user.set_password(passA)
    user.registered_on=datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    send_validate_email(user)

    submission_=dbc.Alert( "Success! To finish your registration please check your email." , style={"margin-top":"20px"},color="success")
    return first_name_,last_name_,username_, email_,passA_,passB_,agree_,submission_
    

    
    # dbc.Alert( first_name , color="warning"), dbc.Alert( last_name , color="warning"), dbc.Alert( email , color="warning"), dbc.Alert( passA , color="warning"), dbc.Alert( passB , color="warning"), dbc.Alert( agree , color="warning"), dbc.Alert( "submission" , color="warning")



