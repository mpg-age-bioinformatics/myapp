from cycshare import app, db
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from cycshare.models import User
from cycshare.email import send_validate_email
from datetime import datetime
from ._utils import META_TAGS, check_email, password_check
from flask_login import current_user

dashapp = dash.Dash("contact",url_base_pathname='/contact/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title="cycshare")# , assets_folder="/flaski/flaski/static/dash/")

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
    dbc.Col( md=4),
    dbc.Col( [ dbc.Card(  dbc.Form([ dcc.Location(id='url', refresh=False),
                                    html.H2("Contact", style={'textAlign': 'center'} ),
                                    dbc.Row([ 
                                        dbc.Col([ firstname_input,html.Div(id="firstname-feedback")] ),  
                                        dbc.Col([ lastname_input,html.Div(id="lastname-feedback")] )] ),
                                    email_input,
                                    html.Div(id="email-feedback"),
                                    message,
                                    html.Div(id="message-feedback"),
                                    html.Button(id='submit-button-state', n_clicks=0, children='Send', style={"width":"auto","margin-top":4, "margin-bottom":4}),
                                    html.Div(id="submission-feedback"),
                                ])
                        , body=True), footer ],
             md=4, align="center",style={ "margin-left":2, "margin-right":2 }),
    dbc.Col( md=4),
],
align="center",
style={"min-height": "100vh", 'verticalAlign': 'center'})

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
    if 


@dashapp.callback(
    Output('firstname-feedback', 'children'),
    Output('lastname-feedback', 'children'),
    Output('email-feedback', 'children'),
    Output('message-feedback', 'children'),
    Input('submit-button-state', 'n_clicks'),
    State('first_name', 'value'),
    State('last_name', 'value'),
    State('input-email', 'value'),
    State('input-text', 'value'))
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
        return irst_name_ , last_name_, email_, message_

    #### keep on here
    #### call send email function
    #### reset all the values
    #### create subpath for sent
    