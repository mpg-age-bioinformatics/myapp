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
        {'label': " I've read the", 'value': 'useragree'},
    ],
    value=[], 
    style={"margin-left":"15px"}
)


#[dbc.Form([email_input, password_input])]
dashapp.layout=dbc.Row( [
    dbc.Col( md=4),
    dbc.Col( [ html.Div(id="app_access"),
               dbc.Card(  dbc.Form([ html.H2("Register", style={'textAlign': 'center'} ),
                                    dbc.Row([ 
                                        dbc.Col([ firstname_input,html.Div(id="firstname-feedback")] ),  
                                        dbc.Col([ lastname_input,html.Div(id="lastname-feedback")] )] ),
                                    email_input,
                                    html.Div(id="email-feedback"),
                                    password_input,
                                    html.Div(id="pass-feedback"),
                                    password_input_2,
                                    html.Div(id="pass2-feedback"),
                                    dbc.Row([ read , 
                                              html.A("User Agreement and Data Privacy Statment.", href="https://www.sapo.pt",style={"margin-left":"4px",'whiteSpace': 'pre-wrap'})]),
                                    html.Div(id="checkbox-feedback"),
                                    html.Button(id='submit-button-state', n_clicks=0, children='Submit', style={"width":"auto","margin-top":4, "margin-bottom":4}),
                                    html.Div(id="submission-feedback"),
                                ])
                        , body=True)],
             md=4, align="center"),
    dbc.Col( md=4),
],
align="center",
style={"min-height": "100vh", 'verticalAlign': 'center'})

@dashapp.callback(
    Output('firstname-feedback', 'children'),
    Output('lastname-feedback', 'children'),
    Output('email-feedback', 'children'),
    Output('pass-feedback', 'children'),
    Input('submit-button-state', 'n_clicks'),
    State('first_name', 'value'),
    State('last_name', 'value'),
    State('input-email', 'value'),
    State('input-password', 'value'),
    prevent_initial_call=True
    )
def test_out(n_clicks,first_name, last_name, email,passA, passB):
    return dbc.Alert( first_name , color="warning"), dbc.Alert( last_name , color="warning"), dbc.Alert( email , color="warning"),dbc.Alert( passA , color="warning")



