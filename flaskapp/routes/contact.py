from flaskapp import app, db
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flaskapp.models import User
from flaskapp.email import send_contact
from datetime import datetime
from ._utils import META_TAGS ,check_email, navbar_A
from flask_login import current_user

dashapp = dash.Dash("contact",url_base_pathname='/contact/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])

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

message=dbc.FormGroup(
    [
        dbc.Label("Message", html_for="input-text"),
        dcc.Textarea( id='input-text', placeholder="your message ..",style={ "width":"100%", 'height': 250 } ),
    ]
)

footer=html.Div([
    dbc.Row( 
        html.Footer( [ html.A("Login", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/login/"),
                     html.A("Forgot Password", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/forgot/"),
                     html.A("Register", style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px"}, href="/register/")] , 
        style={"margin-top": 5, "margin-bottom": 5, "margin-left": "20px"},
        ),
        style={"justify-content":"center"}
        )
    ])

dashapp.layout=dbc.Row( [
    dbc.Col( [ dbc.Card(  dbc.Form([ dcc.Location(id='url', refresh=False),
                                    html.Div(id="page-redirect"),
                                    html.H2("Contact", style={'textAlign': 'center'} ),
                                    html.Div(id="submission-feedback"),
                                    dbc.Row([ 
                                        dbc.Col([ firstname_input,html.Div(id="firstname-feedback")] ),  
                                        dbc.Col([ lastname_input,html.Div(id="lastname-feedback")] )] ),
                                    email_input,
                                    html.Div(id="email-feedback"),
                                    message,
                                    html.Div(id="message-feedback"),
                                    html.Button(id='submit-button-state', n_clicks=0, children='Send', style={"width":"auto","margin-top":4, "margin-bottom":4}),
                                ])
                        , body=True), footer ],
             md=8, lg=6, xl=4, align="center",style={ "margin-left":2, "margin-right":2 ,'margin-bottom':"50px"}),
    navbar_A
],
align="center",
justify="center",
style={"min-height": "95vh", 'verticalAlign': 'center'})

@dashapp.callback(
    Output('first_name', 'value'),
    Output('last_name', 'value'),
    Output('input-email', 'value') ,
    Input('url', 'pathname'))
def check_logged(pathname):
    if current_user:
        if current_user.is_authenticated:
            return current_user.firstname, current_user.lastname, current_user.email
    return None, None, None

### need to finish this bit
@dashapp.callback(
    Output('submission-feedback', 'children'),
    Input('url', 'pathname'))
def check_sent(pathname):
    if pathname == "/contact/sent/":
        return dbc.Alert( "You're message has been sent." ,color="success")

@dashapp.callback(
    Output('firstname-feedback', 'children'),
    Output('lastname-feedback', 'children'),
    Output('email-feedback', 'children'),
    Output('message-feedback', 'children'),
    Output('page-redirect', 'children'),
    Input('submit-button-state', 'n_clicks'),
    State('first_name', 'value'),
    State('last_name', 'value'),
    State('input-email', 'value'),
    State('input-text', 'value'),
    prevent_initial_call=True)
def send_contact_email(n_clicks, firstname, lastname, email, message):
    first_name_=None
    last_name_=None
    email_=None
    message_=None

    if not firstname:
        first_name_=dbc.Alert( "*required" ,color="warning") # style={"font-size":"10px"}
    if not lastname:
        last_name_=dbc.Alert( "*required" ,color="warning")
    if not email:
        email_=dbc.Alert( "*required" ,color="warning")
    elif not check_email(email):
        email_=dbc.Alert( "invalid email address" ,color="warning")
    if not message:
        message_=dbc.Alert( "*required" ,color="warning")

    if first_name_ or last_name_ or email_ or message_ :
        return first_name_ , last_name_, email_, message_, None

    # send_contact(firstname, lastname, email, message)

    return first_name_ , last_name_, email_, message_, dcc.Location(pathname="/contact/sent/", id='index')
    