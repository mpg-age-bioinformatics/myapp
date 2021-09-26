from cycshare import app
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import uuid
from werkzeug.utils import secure_filename
import json
from flask import session
from ._utils import META_TAGS

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



email_input = dbc.FormGroup(
    [
        dbc.Label("Email", html_for="example-email"),
        dbc.Input(type="email", id="example-email", placeholder="Enter email"),
    ]
)

password_input = dbc.FormGroup(
    [
        dbc.Label("Password", html_for="example-password"),
        dbc.Input(
            type="password",
            id="example-password",
            placeholder="Enter password",
        ),
    ]
)

password_input_2 = dbc.FormGroup(
    [
        dbc.Label("Repeat Password", html_for="example-password-2"),
        dbc.Input(
            type="password",
            id="example-password-2",
            placeholder="Enter password again",
        ),
    ]
)

read=dcc.Checklist(
    options=[
        {'label': " I've read the", 'value': 'useragree'},
    ],
    value=[], 
    style={"margin-left":"15px"}
)


#[dbc.Form([email_input, password_input])]
dashapp.layout=dbc.Row( [
    dbc.Col( md=4),
    dbc.Col( dbc.Card(  dbc.Form([ html.H2("Register", style={'textAlign': 'center'} ),
                                    dbc.Row([ 
                                        dbc.Col(firstname_input),  
                                        dbc.Col(lastname_input)] ),
                                    email_input,
                                    html.Div(id="email-feedback"),
                                    password_input,
                                    html.Div(id="pass-feedback"),
                                    password_input_2,
                                    html.Div(id="pass2-feedback"),
                                    dbc.Row([ read , 
                                              html.A("User Agreement and Data Privacy Statment.", href="https://www.sapo.pt",style={"margin-left":"4px",'whiteSpace': 'pre-wrap'})]),
                                    html.Div(id="checkbox-feedback"),
                                    html.Button(id='submit-button-state', n_clicks=0, children='Submit', style={"width":"auto","margin-top":4, "margin-bottom":4})
                                ])
                        , body=True),
             md=4, align="center"),
    dbc.Col( md=4),
],
align="center",
style={"min-height": "100vh", 'verticalAlign': 'center'})
